"""
rag/retriever.py

Pipeline de recherche hybride (BM25 + FAISS) sur le dataset ISPM,
extrait et adapté du notebook ORIENT_IA_RAG.ipynb pour être utilisable
comme module Python "normal" (hors Colab) par l'agent LangChain.

Point d'entrée principal pour le reste du code : `retrieve_context(query)`.

Le chargement du fichier Excel + la construction des embeddings/index
sont coûteux (quelques secondes à quelques dizaines de secondes selon
la taille du dataset et si le modèle d'embedding est déjà en cache).
On ne veut donc PAS refaire ce travail à chaque appel de l'outil par
l'agent : tout est encapsulé dans un singleton `_RagIndex`, initialisé
paresseusement au premier appel de `retrieve_context`.
"""

from __future__ import annotations

import os
import re
import json
import threading

import pandas as pd
import numpy as np
from unidecode import unidecode


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Chemin du fichier Excel source. Surchargeable via variable d'environnement
# pour ne pas coder en dur un chemin Google Drive/Colab.
EXCEL_PATH = os.path.join(os.path.dirname(__file__), "ORIENT_IA_Dataset_Niveaux_1_a_5.xlsx")

# Colonnes exclues du texte indexé (bruit lexical/sémantique), gardées comme métadonnées.
COLONNES_METADONNEES = {"Source", "Date_Consultation", "Statut_Source", "Niveau_Confiance", "Notes_Incertaines"}

ALIAS_CODES = {"ISAIIA": "ISAIA"}  # coquille repérée dans la feuille 'Compétences développées'

STOPWORDS_FR = {
    "le", "la", "les", "de", "des", "du", "un", "une", "et", "en", "a", "au", "aux", "d", "l",
    "que", "qui", "quoi", "dont", "est", "sont", "pour", "dans", "sur", "par", "avec", "ce",
    "cette", "ces", "son", "sa", "ses", "je", "tu", "il", "elle", "nous", "vous", "ils", "elles",
    "quel", "quelle", "quels", "quelles", "y", "se", "ne", "pas",
}

EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


# ---------------------------------------------------------------------------
# Fonctions utilitaires (identiques à la logique du notebook)
# ---------------------------------------------------------------------------

def nettoyer_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].apply(lambda v: v.strip() if isinstance(v, str) else v)
            df[col] = df[col].replace(r"^\s*$", pd.NA, regex=True)
    return df


def normaliser_code(code):
    if pd.isna(code):
        return None
    c = re.sub(r"\s+", "", str(code)).upper()
    return ALIAS_CODES.get(c, c)


def tokenize_fr(text: str) -> list[str]:
    text_clean = unidecode(text.lower())
    text_clean = re.sub(r"[^\w\s]", " ", text_clean)
    return [w for w in text_clean.split() if len(w) > 1 and w not in STOPWORDS_FR]


# ---------------------------------------------------------------------------
# Index RAG (singleton, chargement paresseux)
# ---------------------------------------------------------------------------

class _RagIndex:
    """Encapsule le chargement des données + la construction de l'index hybride."""

    def __init__(self):
        self.sheets_dict: dict[str, pd.DataFrame] = {}
        self.chunks: list[dict] = []
        self.bm25 = None
        self.embedding_model = None
        self.faiss_index = None
        self._ready = False

    # -- chargement des données -------------------------------------------------

    def _load_excel(self):
        if not os.path.exists(EXCEL_PATH):
            raise FileNotFoundError(
                f"Fichier introuvable : '{EXCEL_PATH}'. "
                "Placez le fichier ORIENT_IA_Dataset_Niveaux_1_a_5.xlsx au bon endroit, "
                "ou définissez la variable d'environnement ORIENT_IA_EXCEL_PATH."
            )
        xls = pd.ExcelFile(EXCEL_PATH)
        sheets_dict_raw = {s: pd.read_excel(xls, s) for s in xls.sheet_names}
        self.sheets_dict = {name: nettoyer_dataframe(df) for name, df in sheets_dict_raw.items()}

        for _name, _df in self.sheets_dict.items():
            for _col in _df.columns:
                if _col.startswith("Code_Parcours"):
                    _df[_col] = _df[_col].apply(normaliser_code)

        def get_sheet(fragment):
            for s in self.sheets_dict:
                if fragment.lower() in s.lower():
                    return s
            raise KeyError(f"Aucune feuille trouvée contenant '{fragment}'. Feuilles dispo : {list(self.sheets_dict.keys())}")

        self.SHEET_FORMATIONS = get_sheet("Formations_Matieres")
        self.SHEET_DEBOUCHES = get_sheet("Débouchés")
        self.SHEET_RELATION = get_sheet("Relation")
        self.SHEET_PASSERELLES = get_sheet("passerelle")
        self.SHEET_CONDITIONS = get_sheet("Conditions")
        self.SHEET_COMPETENCES = get_sheet("Compétences développées")

    # -- construction des chunks --------------------------------------------------

    def _construire_chunks_lignes(self) -> list[dict]:
        chunks = []
        for sheet_name, df in self.sheets_dict.items():
            if sheet_name == "00_README":
                continue
            for index, row in df.iterrows():
                if row.dropna().empty:
                    continue

                code_parcours = row.get("Code_Parcours", row.get("Code_Parcours_Origine", None))
                mention = row.get("Mention", row.get("Mention_Origine", None))
                niveau = row.get("Niveau", None)
                source = row.get("Source", None)

                champs = []
                for col in df.columns:
                    if col in COLONNES_METADONNEES:
                        continue
                    val = row[col]
                    if pd.notna(val) and str(val).strip() != "":
                        champs.append(f"{col}: {val}")

                if not champs:
                    continue

                row_text = f"FEUILLE: {sheet_name} | " + " | ".join(champs)
                citation_ref = f"[Feuille: '{sheet_name}' | Ligne {index + 2}]"

                chunks.append({
                    "id": len(chunks),
                    "text": row_text,
                    "citation": citation_ref,
                    "sheet": sheet_name,
                    "row_idx": index + 2,
                    "code_parcours": code_parcours if pd.notna(code_parcours) else None,
                    "mention": str(mention) if pd.notna(mention) else None,
                    "niveau": str(niveau) if pd.notna(niveau) else None,
                    "source_officielle": str(source) if pd.notna(source) else None,
                    "type": "ligne",
                })
        return chunks

    def _construire_chunks_synthese_parcours(self) -> list[dict]:
        df_form = self.sheets_dict[self.SHEET_FORMATIONS]
        df_comp = self.sheets_dict[self.SHEET_COMPETENCES]
        df_deb = self.sheets_dict[self.SHEET_DEBOUCHES]
        df_rel = self.sheets_dict[self.SHEET_RELATION]

        chunks = []
        for code in sorted(df_form["Code_Parcours"].dropna().unique()):
            lignes = df_form[df_form["Code_Parcours"] == code].sort_values("Niveau")
            if lignes.empty:
                continue

            premiere = lignes.iloc[0]
            mention = premiere.get("Mention")
            nom_parcours = premiere.get("Nom_Parcours")
            description = premiere.get("Description_Parcours")

            matieres_par_niveau = []
            for _, l in lignes.iterrows():
                if pd.notna(l.get("Matière")):
                    matieres_par_niveau.append(f"Niveau {l.get('Niveau')} ({l.get('Diplôme')}): {l.get('Matière')}")

            comp_row = df_comp[df_comp["Code_Parcours"] == code]
            competences_dev = comp_row.iloc[0].get("Compétences développées") if not comp_row.empty else None

            deb_row = df_deb[df_deb["Code_Parcours"] == code]
            metiers = deb_row.iloc[0].get("Metiers_Estimes") if not deb_row.empty else None

            rel_row = df_rel[df_rel["Code_Parcours"] == code]
            matieres_pivot = rel_row.iloc[0].get("Matieres_Pivot") if not rel_row.empty else None
            comp_tech = rel_row.iloc[0].get("Competences_Techniques") if not rel_row.empty else None
            comp_trans = rel_row.iloc[0].get("Competences_Transversales") if not rel_row.empty else None

            parties = [f"SYNTHÈSE PARCOURS {code} ({nom_parcours}, mention {mention})"]
            if pd.notna(description):
                parties.append(f"Description: {description}")
            if matieres_par_niveau:
                parties.append("Programme par niveau: " + " ; ".join(matieres_par_niveau))
            if pd.notna(competences_dev):
                parties.append(f"Compétences développées: {competences_dev}")
            if pd.notna(matieres_pivot):
                parties.append(f"Matières pivot: {matieres_pivot}")
            if pd.notna(comp_tech):
                parties.append(f"Compétences techniques: {comp_tech}")
            if pd.notna(comp_trans):
                parties.append(f"Compétences transversales: {comp_trans}")
            if pd.notna(metiers):
                parties.append(f"Débouchés / métiers estimés: {metiers}")

            chunks.append({
                "id": None,
                "text": " | ".join(parties),
                "citation": f"[Synthèse consolidée du parcours {code}]",
                "sheet": "synthese",
                "row_idx": None,
                "code_parcours": code,
                "mention": str(mention) if pd.notna(mention) else None,
                "niveau": None,
                "source_officielle": None,
                "type": "synthese",
            })
        return chunks

    # -- construction de l'index -------------------------------------------------

    def build(self):
        """Charge les données et construit BM25 + FAISS. Idempotent."""
        if self._ready:
            return

        # Imports coûteux/optionnels faits ici (pas au niveau du module) pour que
        # le reste de l'agent (routing, sécurité) puisse tourner même si ces libs
        # ne sont pas encore installées dans l'environnement de dev.
        from sentence_transformers import SentenceTransformer
        from rank_bm25 import BM25Okapi
        import faiss

        self._load_excel()

        self.chunks = self._construire_chunks_lignes() + self._construire_chunks_synthese_parcours()
        for i, c in enumerate(self.chunks):
            c["id"] = i

        self.CODES_CONNUS = sorted(
            self.sheets_dict[self.SHEET_FORMATIONS]["Code_Parcours"].dropna().unique().tolist(),
            key=len, reverse=True,
        )

        tokenized_corpus = [tokenize_fr(c["text"]) for c in self.chunks]
        self.bm25 = BM25Okapi(tokenized_corpus)

        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        corpus_embeddings = self.embedding_model.encode(
            [c["text"] for c in self.chunks], show_progress_bar=False
        ).astype("float32")

        faiss.normalize_L2(corpus_embeddings)
        dimension = corpus_embeddings.shape[1]
        self.faiss_index = faiss.IndexFlatIP(dimension)
        self.faiss_index.add(corpus_embeddings)

        self._ready = True

    # -- détection du code parcours cité dans une question -----------------------

    def detecter_code_parcours(self, question: str) -> str | None:
        q_norm = unidecode(question.upper())
        for code in self.CODES_CONNUS:
            if re.search(rf"\b{re.escape(code)}\b", q_norm):
                return code
        return None

    # -- recherche hybride ---------------------------------------------------

    def recherche_hybride(self, query: str, top_k: int = 5, k_rrf: int = 60, code_parcours_filtre: str | None = None):
        import faiss  # noqa: F401 (déjà importé dans build(), mais explicite ici)

        token_query = tokenize_fr(query)
        bm25_scores = self.bm25.get_scores(token_query)
        bm25_top_indices = np.argsort(bm25_scores)[::-1][: top_k * 4]

        q_vector = self.embedding_model.encode([query]).astype("float32")
        import faiss as _faiss
        _faiss.normalize_L2(q_vector)
        _, faiss_top_indices = self.faiss_index.search(q_vector, top_k * 4)
        faiss_top_indices = faiss_top_indices[0]

        rrf_scores: dict[int, float] = {}
        for rank, idx in enumerate(bm25_top_indices):
            rrf_scores[idx] = rrf_scores.get(idx, 0.0) + (1.0 / (k_rrf + rank + 1))
        for rank, idx in enumerate(faiss_top_indices):
            rrf_scores[idx] = rrf_scores.get(idx, 0.0) + (1.0 / (k_rrf + rank + 1))

        candidats = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)

        if code_parcours_filtre:
            code_norm = normaliser_code(code_parcours_filtre)
            candidats_filtres = [idx for idx in candidats if self.chunks[idx].get("code_parcours") == code_norm]
            if candidats_filtres:
                candidats = candidats_filtres

        sorted_indices = candidats[:top_k]
        return [{"chunk": self.chunks[idx], "score_rrf": rrf_scores.get(idx, 0.0)} for idx in sorted_indices]


# ---------------------------------------------------------------------------
# Singleton thread-safe
# ---------------------------------------------------------------------------

_index: _RagIndex | None = None
_lock = threading.Lock()


def _get_index() -> _RagIndex:
    global _index
    if _index is None:
        with _lock:
            if _index is None:  # double-check locking
                idx = _RagIndex()
                idx.build()
                _index = idx
    return _index


# ---------------------------------------------------------------------------
# API publique utilisée par l'outil LangChain
# ---------------------------------------------------------------------------

def retrieve_context(query: str, top_k: int = 5, code_parcours_filtre: str | None = None) -> str:
    """
    Recherche hybride (BM25 + FAISS) sur le dataset ISPM et renvoie un contexte
    textuel prêt à être injecté dans un prompt, avec citation systématique de
    la source (feuille + ligne, ou synthèse de parcours) devant chaque extrait.

    Si aucun `code_parcours_filtre` explicite n'est fourni, on tente de détecter
    automatiquement un code de parcours cité dans la question (ex: "IGGLIA")
    pour resserrer la recherche.
    """
    index = _get_index()

    if code_parcours_filtre is None:
        code_parcours_filtre = index.detecter_code_parcours(query)

    results = index.recherche_hybride(query, top_k=top_k, code_parcours_filtre=code_parcours_filtre)

    if not results:
        return "Aucune information trouvée dans la base documentaire ISPM pour cette requête."

    blocs = []
    for r in results:
        c = r["chunk"]
        blocs.append(f"{c['citation']} {c['text']}")

    return "\n---\n".join(blocs)