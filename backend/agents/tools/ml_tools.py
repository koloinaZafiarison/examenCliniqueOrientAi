from langchain_core.tools import tool
from agents.tools.ml_scorer import score_profile
from agents.tools.recommender import recommend_formations


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
    À utiliser lorsque l'utilisateur décrit sa personnalité, son caractère, ses passions
    ou ce qu'il aime faire pour obtenir une recommandation basée sur son profil comportemental.
    """
    # Simulation d'analyse du modèle de personnalité et d'intérêts
    texte = description_personnelle.lower()
    
    # Simulation d'extraction de traits de caractère
    traits_detectes = []
    if any(k in texte for k in ["créatif", "dessin", "design", "art"]):
        traits_detectes.append("Créativité & Design")
    if any(k in texte for k in ["logique", "résoudre", "analytique", "maths"]):
        traits_detectes.append("Esprit Analytique")
    if any(k in texte for k in ["equipe", "parler", "social", "leader", "gestion"]):
        traits_detectes.append("Leadership & Communication")

    # Si aucun trait ou intérêt évident n'est détecté
    if not traits_detectes:
        traits_detectes = ["Profil Polyvalent / Généraliste"]

    # Simulation des recommandations basées sur la personnalité
    simulated_recommendations = {
        "INFO": {
            "nom_filiere": "Informatique & Télécoms",
            "score_compatibilite": "88%",
            "raison": "Forte adéquation avec la résolution de problèmes et la logique."
        },
        "GESTION": {
            "nom_filiere": "Management & Gestion",
            "score_compatibilite": "75%",
            "raison": "Correspondance avec les compétences d'organisation et de communication."
        }
    }

    return {
        "status": "success",
        "traits_et_interets_detectes": traits_detectes,
        "recommendations": simulated_recommendations,
        "source": "Modèle Machine Learning (Personnalité & Intérêts)"
    }