from __future__ import annotations

import json

from langgraph.graph import END, StateGraph
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from src.config import settings
from src.intent_classifier import classify_intent
from src.lead_flow import extract_lead_fields, is_valid_email, missing_required_fields, next_collection_prompt
from src.rag_pipeline import RagEngine, grounded_answer
from src.state import AgentState
from src.tools import append_lead_json, mock_lead_capture


rag_engine = RagEngine()


class _LocalResponse:
    def __init__(self, content: str) -> None:
        self.content = content


class LocalFallbackLLM:
    def invoke(self, payload):
        if isinstance(payload, list):
            text = ""
            for msg in payload:
                if isinstance(msg, HumanMessage):
                    text = msg.content
                    break

            lowered = text.lower()
            if any(token in lowered for token in ("hi", "hello", "hey")) and len(lowered.split()) <= 5:
                return _LocalResponse(json.dumps({"intent": "casual_greeting"}))
            if any(token in lowered for token in ("buy", "sign up", "trial", "subscribe")):
                return _LocalResponse(json.dumps({"intent": "high_intent_lead"}))
            return _LocalResponse(json.dumps({"intent": "product_or_pricing_inquiry"}))

        if isinstance(payload, str):
            # Return a concise grounded summary extracted from prompt context.
            if "Basic Plan" in payload or "$29/month" in payload:
                return _LocalResponse("Basic is $29/month with 10 videos at 720p. Pro is $79/month with unlimited 4K and AI captions.")
            if "refund" in payload.lower() or "support" in payload.lower():
                return _LocalResponse("No refunds after 7 days, and 24/7 support is available only on the Pro plan.")
            return _LocalResponse("Based on the local knowledge base, AutoStream offers Basic and Pro plans with clear feature differences.")

        return _LocalResponse("I can help with AutoStream pricing, features, and signup.")


def _create_llm():
    if settings.google_api_key:
        return ChatGoogleGenerativeAI(
            model=settings.model_name,
            google_api_key=settings.google_api_key,
            temperature=0,
        )
    return LocalFallbackLLM()


llm = _create_llm()


def classify_node(state: AgentState) -> AgentState:
    user_input = state.get("user_input", "")
    intent = classify_intent(user_input, llm)
    state["intent"] = intent
    return state


def chat_node(state: AgentState) -> AgentState:
    user_input = state.get("user_input", "")
    intent = state.get("intent", "product_or_pricing_inquiry")

    if intent == "casual_greeting":
        state["response"] = "Hi. I can help with AutoStream pricing, features, and signup."
        return state

    if intent == "product_or_pricing_inquiry":
        chunks = rag_engine.retrieve(user_input)
        state["retrieved_context"] = chunks
        state["response"] = grounded_answer(llm, user_input, chunks)
        return state

    # high_intent_lead path
    state["response"] = "Great. I can help you get started."
    return state


def lead_collection_node(state: AgentState) -> AgentState:
    fields = {
        "name": state.get("name"),
        "email": state.get("email"),
        "platform": state.get("platform"),
    }
    updated = extract_lead_fields(state.get("user_input", ""), fields)

    state["name"] = updated.get("name")
    state["email"] = updated.get("email")
    state["platform"] = updated.get("platform")

    missing = missing_required_fields(state.get("name"), state.get("email"), state.get("platform"))
    if state.get("email") and not is_valid_email(state["email"] or ""):
        missing = sorted(set(missing + ["email"]))

    state["missing_fields"] = missing

    if missing:
        state["response"] = next_collection_prompt(missing)
    return state


def lead_capture_node(state: AgentState) -> AgentState:
    # Safety guard 1: prevent duplicate submissions.
    if state.get("lead_captured"):
        state["response"] = "Your lead is already captured. Our team will contact you soon."
        return state

    missing = missing_required_fields(state.get("name"), state.get("email"), state.get("platform"))
    if missing:
        state["response"] = next_collection_prompt(missing)
        state["missing_fields"] = missing
        return state

    email = state.get("email") or ""
    if not is_valid_email(email):
        state["response"] = "Please share a valid email address."
        state["missing_fields"] = ["email"]
        return state

    capture_msg = mock_lead_capture(state["name"] or "", email, state["platform"] or "")
    append_lead_json(
        settings.leads_file_path,
        state["name"] or "",
        email,
        state["platform"] or "",
        state.get("session_id", "unknown"),
    )

    state["lead_captured"] = True
    state["capture_result"] = capture_msg
    state["response"] = "Thanks. Your lead has been captured successfully."
    state["missing_fields"] = []
    return state


def route_after_classify(state: AgentState) -> str:
    lead_in_progress = (
        not state.get("lead_captured", False)
        and any(state.get(field) for field in ("name", "email", "platform"))
    )

    if lead_in_progress:
        return "lead_collection"

    intent = state.get("intent", "product_or_pricing_inquiry")
    if intent == "high_intent_lead":
        return "lead_collection"
    return "chat"


def route_after_collection(state: AgentState) -> str:
    if state.get("missing_fields"):
        return "end"
    return "capture"


def build_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("classify", classify_node)
    workflow.add_node("chat", chat_node)
    workflow.add_node("lead_collection", lead_collection_node)
    workflow.add_node("lead_capture", lead_capture_node)

    workflow.set_entry_point("classify")
    workflow.add_conditional_edges(
        "classify",
        route_after_classify,
        {
            "chat": "chat",
            "lead_collection": "lead_collection",
        },
    )
    workflow.add_edge("chat", END)
    workflow.add_conditional_edges(
        "lead_collection",
        route_after_collection,
        {
            "capture": "lead_capture",
            "end": END,
        },
    )
    workflow.add_edge("lead_capture", END)
    return workflow.compile()
