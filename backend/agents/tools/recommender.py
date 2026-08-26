def recommend_formations(responses: dict[str, str], score: dict[str, float]) -> list[dict[str, str]]:
    """Recommandation KNN minimale, remplaçable par le modèle entraîné."""
    text = " ".join(responses.values()).lower()
    label = "Informatique et intelligence artificielle" if any(word in text for word in ("programm", "robot", "techn")) else "Gestion et entrepreneuriat"
    return [{"formation": label, "reason": "Correspondance avec les intérêts déclarés."}]