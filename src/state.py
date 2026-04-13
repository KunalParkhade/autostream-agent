from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict


class AgentState(TypedDict, total=False):
    session_id: str
    user_input: str
    messages: List[Dict[str, str]]
    intent: str
    response: str
    name: Optional[str]
    email: Optional[str]
    platform: Optional[str]
    missing_fields: List[str]
    lead_captured: bool
    capture_result: Optional[str]
    retrieved_context: List[str]
    should_retrieve: bool
    errors: List[str]
    metadata: Dict[str, Any]


def init_state(session_id: str) -> AgentState:
    return {
        "session_id": session_id,
        "messages": [],
        "intent": "product_or_pricing_inquiry",
        "lead_captured": False,
        "name": None,
        "email": None,
        "platform": None,
        "missing_fields": [],
        "errors": [],
        "metadata": {},
    }
