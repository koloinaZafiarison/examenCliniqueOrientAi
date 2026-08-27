import re


# DÉTECTION DES TENTATIVES D'INJECTION

INJECTION_PATTERNS = (
    r"ignore\s+(all|previous|the previous)",
    r"ignore\s+les\s+instructions",
    r"ignore\s+tes\s+instructions",
    r"oublie\s+(les|toutes\s+les)\s+instructions",
    r"system\s+prompt",
    r"system\s+message",
    r"jailbreak",
    r"révèle\s+ton\s+prompt",
    r"montre\s+ton\s+prompt",
)


# DÉTECTION DES MESSAGES SENSIBLES
SENSITIVE_PATTERNS = (
    r"\bje\s+veux\s+mourir\b",
    r"\bje\s+veux\s+mourrir\b",
    r"\bje\s+veux\s+me\s+suicider\b",
    r"\bje\s+vais\s+me\s+suicider\b",
    r"\bje\s+vais\s+me\s+tuer\b",
    r"\bje\s+veux\s+me\s+tuer\b",
    r"\bje\s+veux\s+en\s+finir\b",
    r"\ben\s+finir\s+avec\s+ma\s+vie\b",
    r"\bmettre\s+fin\s+à\s+mes\s+jours\b",
)


def validate_input(text: str) -> str:
    """
    Valide et nettoie le message utilisateur.

    Retourne le message nettoyé.

    Lève ValueError si une tentative d'injection
    est détectée.
    """

    text = str(text).strip()

    if not text:
        raise ValueError("Le message ne peut pas être vide.")

    if any(
        re.search(pattern, text, re.IGNORECASE)
        for pattern in INJECTION_PATTERNS
    ):
        raise ValueError("Entrée refusée.")

    return text[:2000]


def is_sensitive_message(text: str) -> bool:
    """
    Détecte les messages nécessitant une réponse de sécurité.

    Cette fonction doit être appelée AVANT l'agent LLM.
    """

    text = str(text).strip()

    return any(
        re.search(pattern, text, re.IGNORECASE)
        for pattern in SENSITIVE_PATTERNS
    )