from pathlib import Path


def score_profile(responses: dict[str, str]) -> dict[str, float]:
    """Charge XGBoost si un modèle existe, sinon fournit un score neutre."""
    model_path = Path(__file__).parents[3] / "ml" / "models" / "profile_scorer.joblib"
    if model_path.exists():
        import joblib
        model = joblib.load(model_path)
        return {"confidence": float(model.predict_proba([[len(responses)]])[0].max())}
    return {"confidence": 0.0, "status": "model_not_trained"}