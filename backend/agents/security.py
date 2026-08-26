import re

INJECTION_PATTERNS = (r"ignore\s+(all|previous)", r"system\s+prompt", r"jailbreak")


def validate_input(responses: dict[str, str]) -> dict[str, str]:
    cleaned = {}
    for key, value in responses.items():
        text = str(value).strip()
        if any(re.search(pattern, text, re.IGNORECASE) for pattern in INJECTION_PATTERNS):
            raise ValueError("Entrée refusée")
        cleaned[str(key)[:120]] = text[:2000]
    return cleaned