from agents.security import validate_input
from agents.tools.anomaly_detector import detect_anomaly
from agents.tools.ml_scorer import score_profile
from agents.tools.recommender import recommend_formations
from rag.retriever import retrieve_context


def orienter(responses: dict[str, str]) -> dict:
    """Orchestre les signaux sans jamais produire de décision discriminatoire."""
    clean = validate_input(responses)
    score = score_profile(clean)
    return {
        "recommendations": recommend_formations(clean, score),
        "score": score,
        "anomaly": detect_anomaly(clean),
        "context": retrieve_context(clean),
    }