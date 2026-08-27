import re
import pandas as pd
import joblib
from huggingface_hub import hf_hub_download

# 1. CONFIGURATION HUGGING FACE
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
    'math_score', 'history_score', 'physics_score', 
    'chemistry_score', 'biology_score', 'english_score', 'geography_score'
]

# 2. LOGIQUE DU SCORER
def extraire_notes_regex(texte: str) -> dict:
    """Extrait les notes mentionnées dans le texte de l'utilisateur."""
    notes = {}
    patterns = {
        'math_score': r'maths?[:\s]+(\d+)',
        'physics_score': r'physique[:\s]+(\d+)',
        'chemistry_score': r'chimie[:\s]+(\d+)',
        'biology_score': r'biologie[:\s]+(\d+)',
        'english_score': r'anglais[:\s]+(\d+)',
        'history_score': r'histoire[:\s]+(\d+)',
        'geography_score': r'géo(?:graphie)?[:\s]+(\d+)'
    }
    for col, pat in patterns.items():
        match = re.search(pat, texte, re.IGNORECASE)
        if match:
            notes[col] = float(match.group(1))
    return notes


def score_profile(profile_dict: dict) -> dict:
    """
    Analyse la description, extrait les notes et calcule les probabilités de carrières.
    """
    texte = profile_dict.get("description", "")
    notes_extraites = extraire_notes_regex(texte)

    # Si aucune note n'est détectée
    if not notes_extraites:
        return {
            "has_scores": False,
            "notes_extraites": {},
            "probas_carriere": {}  # Correction : clé alignée avec la réponse avec notes
        }

    # Préparation du DataFrame
    ligne = {col: notes_extraites.get(col, None) for col in score_cols}
    df_input = pd.DataFrame([ligne])
    
    # Imputation
    df_input_imputed = pd.DataFrame(imputer.transform(df_input), columns=score_cols)

    # Prédiction des probabilités par métier
    probas = model.predict_proba(df_input_imputed)[0]
    proba_par_carriere = dict(zip(label_encoder.classes_, probas))

    return {
        "has_scores": True,
        "notes_extraites": notes_extraites,
        "probas_carriere": proba_par_carriere
    }