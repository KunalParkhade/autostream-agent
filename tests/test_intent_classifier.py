from src.intent_classifier import classify_intent


class DummyResponse:
    def __init__(self, content: str):
        self.content = content


class DummyLLM:
    def __init__(self, content: str):
        self._content = content

    def invoke(self, _messages):
        return DummyResponse(self._content)


def test_rule_override_high_intent():
    llm = DummyLLM('{"intent":"casual_greeting"}')
    assert classify_intent("I want to sign up now", llm) == "high_intent_lead"


def test_strict_json_parse_success():
    llm = DummyLLM('{"intent":"casual_greeting"}')
    assert classify_intent("hello there", llm) == "casual_greeting"


def test_json_parse_fallback_default():
    llm = DummyLLM("not-json")
    assert classify_intent("tell me pricing", llm) == "product_or_pricing_inquiry"
