from __future__ import annotations

import re
from typing import Dict, List, Optional


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_valid_email(value: str) -> bool:
    return bool(EMAIL_PATTERN.match(value.strip()))


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

    if "name is" in lowered:
        name_part = text.lower().split("name is", 1)[1].strip()
        if name_part:
            updated["name"] = name_part.split()[0].strip(",.?!").title()
    elif "i am" in lowered:
        name_part = text.lower().split("i am", 1)[1].strip()
        if name_part:
            updated["name"] = name_part.split()[0].strip(",.?!").title()

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
