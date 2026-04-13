from pathlib import Path

from src.config import settings
from src.service import AgentService
from src.state import init_state


def test_state_memory_initialization():
    state = init_state("abc")
    assert state["session_id"] == "abc"
    assert state["lead_captured"] is False
    assert state["messages"] == []


def test_missing_email_flow():
    agent = AgentService()
    result = agent.chat("s-missing-email", "I want to sign up for Pro on YouTube. My name is Kunal")
    assert "email" in result["missing_fields"]


def test_invalid_email_flow():
    agent = AgentService()
    result = agent.chat(
        "s-invalid-email",
        "I want to sign up. My name is Kunal and my email is invalid-email for YouTube",
    )
    assert "email" in result["missing_fields"]


def test_repeated_high_intent_no_duplicate_capture(tmp_path: Path):
    leads_file = tmp_path / "leads.json"
    leads_file.write_text("[]\n", encoding="utf-8")
    object.__setattr__(settings, "leads_file_path", leads_file)

    agent = AgentService()
    first = agent.chat(
        "s-repeat",
        "I want to sign up now. My name is Kunal, email kunal@email.com, for YouTube",
    )
    assert first["lead_captured"] is True

    second = agent.chat("s-repeat", "I want to sign up again")
    assert second["lead_captured"] is True
    assert "already captured" in second["response"].lower()


def test_random_chat_after_capture(tmp_path: Path):
    leads_file = tmp_path / "leads_after_capture.json"
    leads_file.write_text("[]\n", encoding="utf-8")
    object.__setattr__(settings, "leads_file_path", leads_file)

    agent = AgentService()
    agent.chat(
        "s-random",
        "I want to buy Pro. My name is Kunal, email kunal@email.com, platform YouTube",
    )
    result = agent.chat("s-random", "How are you?")
    assert isinstance(result.get("response", ""), str)
