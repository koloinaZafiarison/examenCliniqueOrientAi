def detect_anomaly(responses: dict[str, str]) -> dict[str, object]:
    """Point d'extension Isolation Forest pour repérer des réponses atypiques."""
    return {"is_anomaly": False, "method": "isolation_forest", "status": "placeholder"}