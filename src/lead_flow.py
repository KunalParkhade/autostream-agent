from __future__ import annotations

import re
from typing import Dict, List, Optional


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
NAME_TOKEN_PATTERN = re.compile(r"^[A-Za-z][A-Za-z'\-]{1,29}$")

# Tokens that commonly follow "I am" in high-intent/product phrases, not self-identification.
NON_NAME_TOKENS = {
    "ready",
    "interested",
    "looking",
    "trying",
    "planning",
    "here",
    "available",
}


def is_valid_email(value: str) -> bool:
    return bool(EMAIL_PATTERN.match(value.strip()))


def _extract_name_from_name_is(text: str) -> Optional[str]:
    match = re.search(r"\bname is\s+([A-Za-z][A-Za-z'\-]{1,29})", text, flags=re.IGNORECASE)
    if not match:
        return None
    return match.group(1).strip(",.?!").title()


def _extract_name_from_i_am(text: str) -> Optional[str]:
    match = re.search(r"\bi am\s+([A-Za-z][A-Za-z'\-]{1,29})", text, flags=re.IGNORECASE)
    if not match:
        return None

    candidate = match.group(1).strip(",.?!")
    tail = text[match.end() :].strip().lower()
    if not NAME_TOKEN_PATTERN.match(candidate):
        return None
    if candidate.lower() in NON_NAME_TOKENS:
        return None
    if tail.startswith("to "):
        return None

    return candidate.title()


def extract_lead_fields(text: str, current: Dict[str, Optional[str]]) -> Dict[str, Optional[str]]:
    updated = dict(current)

    # Lightweight extraction to keep behavior deterministic for assignment demo.
    words = text.split()
    for word in words:
        cleaned = word.strip(",.?!")
        if "@" in cleaned and "." in cleaned and is_valid_email(cleaned):
            updated["email"] = cleaned

    lowered = text.lower()
    if "youtube" in lowered:
        updated["platform"] = "YouTube"
    elif "instagram" in lowered:
        updated["platform"] = "Instagram"
    elif "tiktok" in lowered:
        updated["platform"] = "TikTok"
    elif "linkedin" in lowered:
        updated["platform"] = "LinkedIn"

    explicit_name = _extract_name_from_name_is(text)
    if explicit_name:
        updated["name"] = explicit_name
    else:
        iam_name = _extract_name_from_i_am(text)
        if iam_name:
            updated["name"] = iam_name

    return updated


def missing_required_fields(name: Optional[str], email: Optional[str], platform: Optional[str]) -> List[str]:
    missing = []
    if not name:
        missing.append("name")
    if not email:
        missing.append("email")
    if not platform:
        missing.append("platform")
    return missing


def next_collection_prompt(missing_fields: List[str]) -> str:
    if not missing_fields:
        return ""
    if len(missing_fields) == 1:
        field = missing_fields[0]
        return f"Please share your {field}."

    pretty_fields = ", ".join(missing_fields[:-1]) + f" and {missing_fields[-1]}"
    return f"Please share your {pretty_fields}."
