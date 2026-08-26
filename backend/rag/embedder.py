def embed(texts: list[str]) -> list[list[float]]:
    """Interface Sentence-Transformers; le modèle est injecté en production."""
    return [[float(len(text))] for text in texts]