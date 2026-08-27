# ml_tools.py
# Outils LangChain pour l'intégration du modèle ML ORIENT'IA

import json
import joblib
import numpy as np
import pandas as pd
from langchain_core.tools import tool
from pathlib import Path
from typing import List, Dict, Any, Optional
from agents.tools.ml_scorer import score_profile
from agents.tools.recommender import recommend_formations

# ------------------------------------------------------------------
# 1. Configuration et chargement des artefacts
# ------------------------------------------------------------------

# Artefacts stockés dans ml/models à la racine du projet.
PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_DIR = PROJECT_ROOT / "ml" / "models"
MODEL_PATH = MODEL_DIR / "model.pkl"
ENCODERS_PATH = MODEL_DIR / "encoders.pkl"
SCALER_PATH = MODEL_DIR / "scaler.pkl"
METADATA_PATH = MODEL_DIR / "metadata.json"
LABEL_ENCODER_PATH = MODEL_DIR / "label_encoder.pkl"  # optionnel

# Variables globales pour le chargement lazy
_model = None
_encoders = None
_scaler = None
_feature_cols = None
_label_encoder = None
_model_name = None
_priority_cols = None


def _load_artifacts():
    """Charge les artefacts une fois."""
    global _model, _encoders, _scaler, _feature_cols, _label_encoder, _model_name, _priority_cols
    if _model is not None:
        return

    _model = joblib.load(MODEL_PATH)
    _encoders = joblib.load(ENCODERS_PATH)
    _scaler = joblib.load(SCALER_PATH)

    with open(METADATA_PATH, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    _feature_cols = metadata["features"]
    _model_name = metadata.get("model", "LogisticRegression")

    if _model_name == "XGBoost" and LABEL_ENCODER_PATH.exists():
        _label_encoder = joblib.load(LABEL_ENCODER_PATH)
    else:
        _label_encoder = None

    # Définition des colonnes prioritaires pour les questions
    _priority_cols = [
        "Quelle était votre série au Baccalauréat ?",
        "Quelles étaient vos matières préférées au lycée ?"
    ]
    # On filtre pour ne garder que celles qui existent dans feature_cols
    _priority_cols = [c for c in _priority_cols if c in _feature_cols]


# ------------------------------------------------------------------
# 2. Prétraitement (identique au notebook)
# ------------------------------------------------------------------

def _split_and_clean(series, sep=';'):
    """Sépare une chaîne par le séparateur et nettoie les espaces."""
    return series.fillna('').apply(lambda x: [item.strip() for item in str(x).split(sep) if item.strip() != ''])


def _encode_profile(profil_dict: Dict[str, Any]) -> np.ndarray:
    """Encode et normalise un profil pour le modèle ML."""
    _load_artifacts()
    df_profil = pd.DataFrame([profil_dict])

    # S'assurer que toutes les colonnes de feature sont présentes
    for col in _feature_cols:
        if col not in df_profil.columns:
            df_profil[col] = ''

    # Encodage MultiLabelBinarizer
    encoded_parts = []
    for col in _feature_cols:
        lists = _split_and_clean(df_profil[col])
        mlb = _encoders[col]
        encoded = mlb.transform(lists)
        col_names = [f"{col}_{cls}" for cls in mlb.classes_]
        enc_df = pd.DataFrame(encoded, columns=col_names, index=df_profil.index)
        encoded_parts.append(enc_df)

    X_encoded = pd.concat(encoded_parts, axis=1).fillna(0)
    X_scaled = _scaler.transform(X_encoded)
    return X_scaled


# ------------------------------------------------------------------
# 3. Prédiction et recommandations
# ------------------------------------------------------------------

def predict_profil(profil_dict: Dict[str, Any]) -> Dict[str, float]:
    """Retourne les scores pour toutes les filières."""
    _load_artifacts()
    X = _encode_profile(profil_dict)

    if _label_encoder is not None:
        # XGBoost : classes encodées en entiers
        probas = _model.predict_proba(X)[0]
        classes_encoded = _model.classes_
        classes = _label_encoder.inverse_transform(classes_encoded)
        return {cls: float(probas[i]) for i, cls in enumerate(classes)}
    else:
        # Logistic Regression ou Random Forest
        probas = _model.predict_proba(X)[0]
        classes = _model.classes_
        return {cls: float(probas[i]) for i, cls in enumerate(classes)}


def recommander_parcours(profil_dict: Dict[str, Any], top_k: int = 5) -> List[Dict[str, Any]]:
    """Retourne une liste de recommandations structurées."""
    scores = predict_profil(profil_dict)
    sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [
        {"rank": i + 1, "parcours": parcours, "score": round(score, 4)}
        for i, (parcours, score) in enumerate(sorted_items[:top_k])
    ]


def analyser_profil_complet(profil_dict: Dict[str, Any], top_k: int = 5) -> Dict[str, Any]:
    """
    Fonction principale d'analyse de profil.
    Retourne un résultat structuré incluant confiance et points forts.
    """
    _load_artifacts()
    scores = predict_profil(profil_dict)
    sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # Recommandations
    recommendations = [
        {"rank": i + 1, "parcours": parcours, "score": round(score, 4)}
        for i, (parcours, score) in enumerate(sorted_items[:top_k])
    ]

    # Niveau de confiance
    top1_score = sorted_items[0][1] if sorted_items else 0.0
    top2_score = sorted_items[1][1] if len(sorted_items) > 1 else 0.0
    if top1_score - top2_score > 0.2:
        confidence = "high"
    elif top1_score - top2_score > 0.1:
        confidence = "medium"
    else:
        confidence = "low"

    # Points forts : colonnes non vides du profil (limité à 5)
    points_forts = [k for k, v in profil_dict.items() if v and str(v).strip() != ''][:5]

    return {
        "recommendations": recommendations,
        "confidence": confidence,
        "uncertainty": [],
        "points_forts": points_forts,
        "model_version": "1.0"
    }


# ------------------------------------------------------------------
# 4. Outil LangChain principal (modifié pour toujours retourner un résultat)
# ------------------------------------------------------------------

@tool
def analyser_profil_ml(profil_json: str) -> dict:
    """
    Outil principal pour les recommandations d'orientation basées sur le modèle ML.

    Le profil doit être fourni au format JSON avec les clés correspondant aux questions du questionnaire.
    Exemples de clés :
        - 'Quelle était votre série au Baccalauréat ?'
        - 'Quelles étaient vos matières préférées au lycée ?'
        - 'Dans quelles activités pensez-vous être naturellement à l\'aise ?'
        - etc. (voir les colonnes du dataset d'entraînement)

    Même si le profil est incomplet, l'outil retourne une recommandation basée sur les données disponibles,
    avec un indicateur de complétude et les champs manquants.
    """
    # Désérialisation
    try:
        profil_dict = json.loads(profil_json)
    except json.JSONDecodeError:
        return {
            "status": "error",
            "message": "Le profil doit être au format JSON valide."
        }

    if not profil_dict:
        return {
            "status": "error",
            "message": "Le profil ne peut pas être vide."
        }

    _load_artifacts()

    # Vérifier les champs prioritaires manquants
    missing = []
    for col in _priority_cols:
        val = profil_dict.get(col, '')
        if not val or str(val).strip() == '':
            missing.append(col)

    # On fait toujours la prédiction avec les données disponibles
    resultat = analyser_profil_complet(profil_dict, top_k=5)
    resultat["status"] = "success"
    resultat["source"] = f"Modèle ML ({_model_name})"
    
    if missing:
        resultat["completeness"] = "partial"
        resultat["missing_fields"] = missing
        resultat["message"] = "Le profil est incomplet. Les recommandations sont basées sur les informations fournies. Pour une recommandation plus précise, veuillez fournir les champs manquants."
        # On abaisse la confiance si le profil est incomplet
        if resultat["confidence"] == "high":
            resultat["confidence"] = "medium"
        elif resultat["confidence"] == "medium":
            resultat["confidence"] = "low"
    else:
        resultat["completeness"] = "complete"
        resultat["missing_fields"] = []
        resultat["message"] = "Profil complet. Recommandation basée sur toutes les informations disponibles."
    
    return resultat


# ------------------------------------------------------------------
# 5. Outils dépréciés (conservés pour compatibilité)
# ------------------------------------------------------------------

@tool
def analyser_et_scorer_profil(notes_et_interets: str) -> dict:
    """
    À utiliser lorsque l'utilisateur fournit ses notes scolaires ou ses résultats académiques,
    et qu'il souhaite une Recommandation d'Orientation basée sur le modèle ML de notes.
    """
    profile_dict = {"description": notes_et_interets}
    score = score_profile(profile_dict)
    
    # Vérification si des notes ont été trouvées
    if not score.get("has_scores"):
        return {
            "status": "missing_scores",
            "message": "Aucune note chiffrée n'a été détectée dans la demande.",
            "source": "Modèle Machine Learning (Notes)"
        }

    recommendations = recommend_formations(profile_dict, score)
    
    return {
        "status": "success",
        "notes_detectees": score["notes_extraites"],
        "recommendations": recommendations,
        "source": "Modèle Machine Learning (Notes)"
    }


@tool
def analyser_personnalite_et_interets(description_personnelle: str) -> dict:
    """
    [DÉPRÉCIÉ] Utilisez plutôt analyser_profil_ml avec un profil JSON.
    """
    return {
        "status": "deprecated",
        "message": "Cet outil est basé sur une analyse subjective de la personnalité. "
                   "Veuillez utiliser analyser_profil_ml pour une recommandation basée sur le modèle ML."
    }


# ------------------------------------------------------------------
# 6. Test rapide (exécution du script)
# ------------------------------------------------------------------
if __name__ == "__main__":
    # Exemple de profil complet
    test_profil = {
        "Quelle était votre série au Baccalauréat ?": "S",
        "Quelles étaient vos matières préférées au lycée ?": "Mathématiques; Physique; Informatique",
        "Dans quelles matières vous étiez doués?": "Mathématiques; Informatique",
        "Dans quelles activités pensez-vous être naturellement à l'aise ?": "Résoudre des problèmes logiques; Analyser des informations",
        "Parmi les activités suivantes, lesquelles vous attirent le plus ?": "Programmer; Analyser des données",
        "Quel type de problème aimez-vous le plus résoudre ?": "Problèmes logiques et techniques",
        "Quel type d'activité pédagogique vous attire le plus ?": "Programmation; Projets pratiques",
        "Aimez-vous plutôt la pratique ou les leçons (théorie) ?": "Pratique",
        "Quel rythme de travail vous correspond le mieux ?": "Intensif et régulier",
        "Dans quel environnement aimeriez-vous travailler ?": "Entreprise; Startup",
        "Quels sont vos domaines d'intérêt principaux ?": "Technologie; Intelligence artificielle; Data",
        "Préférez-vous travailler principalement": "Seul ou en petite équipe",
        "Qu'est-ce qui est le plus important pour vous dans le choix d'une formation ?": "Développer des compétences professionnelles"
    }

    print("=== Test avec profil complet ===")
    result_complet = analyser_profil_ml(json.dumps(test_profil))
    print(json.dumps(result_complet, indent=2, ensure_ascii=False))

    # Exemple de profil incomplet (manque la série bac et les matières)
    test_incomplet = {
        "Quelles étaient vos matières préférées au lycée ?": "Mathématiques; Physique",
        "Dans quelles activités pensez-vous être naturellement à l'aise ?": "Résoudre des problèmes logiques",
    }
    print("\n=== Test avec profil incomplet ===")
    result_incomplet = analyser_profil_ml(json.dumps(test_incomplet))
    print(json.dumps(result_incomplet, indent=2, ensure_ascii=False))