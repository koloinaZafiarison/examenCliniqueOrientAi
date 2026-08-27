from langchain_core.tools import tool
from backend.agents.tools.ml_scorer import score_profile
from backend.agents.tools.recommender import recommend_formations

@tool
def analyser_et_scorer_profil(notes_et_interets: str) -> dict:
    """
    À utiliser lorsque l'utilisateur fournit ses notes, ses compétences ou ses centres d'intérêt,
    et qu'il souhaite une Recommandation d'Orientation basée sur le modèle Machine Learning.
    """
    # Adaptation si ton score_profile attend un dictionnaire ou une string
    profile_dict = {"description": notes_et_interets}
    score = score_profile(profile_dict)
    recommendations = recommend_formations(profile_dict, score)
    
    return {
        "score": score,
        "recommendations": recommendations,
        "source": "Modèle Machine Learning Statistical Scorer"
    }