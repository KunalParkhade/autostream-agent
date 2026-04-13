import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from src.tools import append_lead_json


def test_append_lead_json_serializes_writes(tmp_path: Path):
    leads_path = tmp_path / "leads.json"

    def _write_one(i: int):
        append_lead_json(
            file_path=leads_path,
            name=f"User{i}",
            email=f"user{i}@example.com",
            platform="YouTube",
            session_id=f"s-{i}",
        )

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(_write_one, range(40)))

    data = json.loads(leads_path.read_text(encoding="utf-8"))
    assert len(data) == 40
    assert {entry["session_id"] for entry in data} == {f"s-{i}" for i in range(40)}
