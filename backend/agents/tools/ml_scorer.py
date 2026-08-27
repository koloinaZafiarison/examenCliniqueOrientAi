import re
import pandas as pd
import joblib
from huggingface_hub import hf_hub_download


# ============================================================
# 1. CONFIGURATION HUGGING FACE
# ============================================================

REPO_ID = "DisMisa/oreint-ia-models"

MODEL_FILENAME = "career_prediction_model.pkl"
LABEL_ENCODER_FILENAME = "label_encoder_recommendation_by_note.pkl"
IMPUTER_FILENAME = "imputer.pkl"


# Chargement automatique des artefacts depuis Hugging Face Hub
model_path = hf_hub_download(
    repo_id=REPO_ID,
    filename=MODEL_FILENAME
)

label_encoder_path = hf_hub_download(
    repo_id=REPO_ID,
    filename=LABEL_ENCODER_FILENAME
)

imputer_path = hf_hub_download(
    repo_id=REPO_ID,
    filename=IMPUTER_FILENAME
)


model = joblib.load(model_path)
label_encoder = joblib.load(label_encoder_path)
imputer = joblib.load(imputer_path)


score_cols = [
    "math_score",
    "history_score",
    "physics_score",
    "chemistry_score",
    "biology_score",
    "english_score",
    "geography_score",
]


# ============================================================
# 2. EXTRACTION DES NOTES
# ============================================================

def extraire_notes_regex(texte: str) -> dict:
    """
    Extrait les notes scolaires depuis une phrase.

    Règles :
    - "16 en maths"       -> 16/20 -> 80/100
    - "16/20 en maths"    -> 16/20 -> 80/100
    - "16 sur 20 en maths"-> 16/20 -> 80/100
    - "8/10 en maths"     -> 8/10  -> 80/100
    - "80/100 en maths"   -> 80/100 -> 80/100
    - "maths : 16"        -> 16/20 -> 80/100

    Si le barème n'est pas précisé :
    - note <= 20 -> barème supposé = 20
    - note > 20  -> ignorée
    """

    notes = {}

    synonymes = {
        "math_score": [
            r"math(?:s|ématiques?)?"
        ],
        "physics_score": [
            r"physique",
            r"phys"
        ],
        "chemistry_score": [
            r"chimie",
            r"chim"
        ],
        "biology_score": [
            r"biologie",
            r"bio"
        ],
        "english_score": [
            r"anglais",
            r"english"
        ],
        "history_score": [
            r"histoire",
            r"hist"
        ],
        "geography_score": [
            r"géographie",
            r"geographie",
            r"géo",
            r"geo"
        ],
    }

    for col, mots in synonymes.items():

        for mot in mots:

            # CAS 1 :
            # "16 en maths"
            # "16/20 en maths"
            # "16 / 20 en maths"
            # "16 sur 20 en maths"

            pattern = (
                r"(\d+(?:[.,]\d+)?)"
                r"(?:\s*(?:/|sur)\s*(\d+(?:[.,]\d+)?))?"
                r"\s+en\s+"
                + mot
                + r"\b"
            )

            match = re.search(
                pattern,
                texte,
                re.IGNORECASE
            )

            if match:

                valeur = float(
                    match.group(1).replace(",", ".")
                )

                bareme_str = match.group(2)

                # Barème explicitement fourni

                if bareme_str:

                    bareme = float(
                        bareme_str.replace(",", ".")
                    )

                    # Note impossible
                    if valeur < 0 or valeur > bareme:
                        continue

                # Aucun barème fourni

                else:

                    # Si la note est <= 20,
                    # on suppose qu'elle est sur 20
                    if valeur <= 20:
                        bareme = 20.0

                    # Une note > 20 sans barème est ambiguë
                    else:
                        continue

                # Normalisation sur 100

                score = valeur * 100 / bareme

                notes[col] = score

                break

            # CAS 2 :
            # "maths : 16"
            # "maths: 16/20"
            # "maths = 16"

            pattern = (
                mot
                + r"\s*(?::|=|-)?\s*"
                r"(\d+(?:[.,]\d+)?)"
                r"(?:\s*(?:/|sur)\s*(\d+(?:[.,]\d+)?))?"
            )

            match = re.search(
                pattern,
                texte,
                re.IGNORECASE
            )

            if match:

                valeur = float(
                    match.group(1).replace(",", ".")
                )

                bareme_str = match.group(2)

                # Barème explicitement fourni

                if bareme_str:

                    bareme = float(
                        bareme_str.replace(",", ".")
                    )

                    if valeur < 0 or valeur > bareme:
                        continue

                # Aucun barème fourni

                else:

                    if valeur <= 20:
                        bareme = 20.0
                    else:
                        continue

                # Normalisation sur 100

                score = valeur * 100 / bareme

                notes[col] = score

                break

    return notes


# ============================================================
# 3. SCORING DU PROFIL
# ============================================================

def score_profile(profile_dict: dict) -> dict:
    """
    Analyse la description, extrait les notes
    et calcule les probabilités de carrières.
    """

    texte = profile_dict.get("description", "")

    notes_extraites = extraire_notes_regex(texte)

    # --------------------------------------------------------
    # Aucune note détectée
    # --------------------------------------------------------

    if not notes_extraites:
        return {
            "has_scores": False,
            "notes_extraites": {},
            "probas_carriere": {}
        }

    # --------------------------------------------------------
    # Préparation du DataFrame
    # --------------------------------------------------------

    ligne = {
        col: notes_extraites.get(col, None)
        for col in score_cols
    }

    df_input = pd.DataFrame([ligne])

    # --------------------------------------------------------
    # Imputation
    # --------------------------------------------------------

    df_input_imputed = pd.DataFrame(
        imputer.transform(df_input),
        columns=score_cols
    )

    # --------------------------------------------------------
    # Prédiction
    # --------------------------------------------------------

    probas = model.predict_proba(
        df_input_imputed
    )[0]

    proba_par_carriere = dict(
        zip(
            label_encoder.classes_,
            probas
        )
    )

    # --------------------------------------------------------
    # Résultat
    # --------------------------------------------------------

    return {
        "has_scores": True,
        "notes_extraites": notes_extraites,
        "probas_carriere": proba_par_carriere
    }