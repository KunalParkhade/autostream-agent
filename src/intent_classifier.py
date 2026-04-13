from __future__ import annotations

import json
from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage


IntentLabel = Literal[
    "casual_greeting",
    "product_or_pricing_inquiry",
    "high_intent_lead",
]


VALID_INTENTS = {
    "casual_greeting",
    "product_or_pricing_inquiry",
    "high_intent_lead",
}


HIGH_INTENT_KEYWORDS = (
    "buy",
    "sign up",
    "signup",
    "get started",
    "start trial",
    "trial",
    "subscribe",
    "purchase",
    "ready to start",
)


GREETING_KEYWORDS = (
    "hi",
    "hello",
    "hey",
    "good morning",
    "good evening",
)


CLASSIFIER_SYSTEM_PROMPT = """You are an intent classifier.
Return only strict JSON with this schema:
{"intent":"casual_greeting|product_or_pricing_inquiry|high_intent_lead"}
No extra keys, no markdown, no prose.
"""


def _rule_override(text: str) -> IntentLabel | None:
    lowered = text.lower()

    if any(keyword in lowered for keyword in HIGH_INTENT_KEYWORDS):
        return "high_intent_lead"

    if any(keyword in lowered for keyword in GREETING_KEYWORDS) and len(lowered.split()) <= 5:
        return "casual_greeting"

    return None


def classify_intent(text: str, llm) -> IntentLabel:
    override = _rule_override(text)
    if override:
        return override

    response = llm.invoke(
        [
            SystemMessage(content=CLASSIFIER_SYSTEM_PROMPT),
            HumanMessage(content=text),
        ]
    )

    parsed_intent = "product_or_pricing_inquiry"
    try:
        payload = json.loads(response.content)
        maybe_intent = payload.get("intent", "").strip()
        if maybe_intent in VALID_INTENTS:
            parsed_intent = maybe_intent
    except (json.JSONDecodeError, AttributeError, TypeError):
        # Fall back to a safe default to keep flow deterministic.
        parsed_intent = "product_or_pricing_inquiry"

    return parsed_intent  # type: ignore[return-value]
