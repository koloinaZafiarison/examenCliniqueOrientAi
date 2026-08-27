from google import genai

from backend.config import settings


def generate_text(prompt: str) -> str:
    """Appelle Gemini avec la clé chargée depuis l'environnement."""
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY n'est pas définie.")

    client = genai.Client(api_key=settings.gemini_api_key)
    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
    )
    return response.text or ""
