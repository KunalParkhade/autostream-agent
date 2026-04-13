from fastapi.testclient import TestClient

from src.api import app


client = TestClient(app)


def test_api_smoke_chat():
    response = client.post(
        "/chat",
        json={"session_id": "s1", "message": "Hi, tell me about pricing"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "response" in payload
    assert "intent" in payload


def test_api_session_state_across_turns():
    session_id = "api-session-1"
    first = client.post(
        "/chat",
        json={"session_id": session_id, "message": "I want to sign up for Pro. My name is Kunal."},
    )
    assert first.status_code == 200
    assert "email" in first.json()["missing_fields"]

    second = client.post(
        "/chat",
        json={"session_id": session_id, "message": "My email is kunal@email.com and platform YouTube."},
    )
    assert second.status_code == 200
    assert second.json()["lead_captured"] is True
