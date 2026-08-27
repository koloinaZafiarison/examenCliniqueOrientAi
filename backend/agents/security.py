import re


INJECTION_PATTERNS = (
    r"ignore\s+(all|previous)",
    r"system\s+prompt",
    r"jailbreak",
)


def validate_input(text: str) -> str:
    """
    Valide et nettoie le message utilisateur.

    Retourne le message nettoyé ou lève ValueError
    si une tentative d'injection est détectée.
    """

    text = str(text).strip()

    if any(
        re.search(pattern, text, re.IGNORECASE)
        for pattern in INJECTION_PATTERNS
    ):
        raise ValueError("Entrée refusée")

    return text[:2000]