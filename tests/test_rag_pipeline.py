from pathlib import Path

from src.rag_pipeline import RagEngine


def test_rag_loads_local_kb(tmp_path: Path):
    kb = tmp_path / "kb.md"
    kb.write_text("Basic plan is $29/month", encoding="utf-8")

    engine = RagEngine()
    docs = engine._load_documents(kb)
    assert docs
    assert "29" in docs[0].page_content
