from src.lead_flow import extract_lead_fields, is_valid_email, missing_required_fields


def test_email_validation():
    assert is_valid_email("user@example.com")
    assert not is_valid_email("not-an-email")


def test_extract_fields_from_text():
    fields = {"name": None, "email": None, "platform": None}
    updated = extract_lead_fields("Hi, I am Kunal and my email is kunal@email.com for YouTube", fields)
    assert updated["name"] == "Kunal"
    assert updated["email"] == "kunal@email.com"
    assert updated["platform"] == "YouTube"


def test_i_am_phrase_not_always_name():
    fields = {"name": None, "email": None, "platform": None}
    updated = extract_lead_fields("I am ready to start trial for YouTube", fields)
    assert updated["name"] is None
    assert updated["platform"] == "YouTube"


def test_missing_fields():
    missing = missing_required_fields("Kunal", None, "YouTube")
    assert missing == ["email"]
