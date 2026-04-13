from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    model_name: str = os.getenv("MODEL_NAME", "gemini-2.5-flash")
    retriever_top_k: int = int(os.getenv("RETRIEVER_TOP_K", "4"))
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    leads_file_path: Path = BASE_DIR / os.getenv("LEADS_FILE_PATH", "data/leads.json")
    kb_file_path: Path = BASE_DIR / os.getenv("KB_FILE_PATH", "data/knowledge_base.md")


settings = Settings()
