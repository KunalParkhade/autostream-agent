from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


def mock_lead_capture(name: str, email: str, platform: str) -> str:
    message = f"Lead captured successfully: {name}, {email}, {platform}"
    print(message)
    return message


def append_lead_json(file_path: Path, name: str, email: str, platform: str, session_id: str) -> Dict[str, Any]:
    record = {
        "name": name,
        "email": email,
        "platform": platform,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
    }

    if not file_path.exists():
        file_path.write_text("[]\n", encoding="utf-8")

    existing = json.loads(file_path.read_text(encoding="utf-8"))
    existing.append(record)
    file_path.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")
    return record
