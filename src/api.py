from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from src.service import service


app = FastAPI(title="AutoStream Social-to-Lead Agent")


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    response: str
    intent: str
    lead_captured: bool
    missing_fields: list[str]


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    result = service.chat(session_id=req.session_id, text=req.message)
    return ChatResponse(
        response=result.get("response", ""),
        intent=result.get("intent", "product_or_pricing_inquiry"),
        lead_captured=result.get("lead_captured", False),
        missing_fields=result.get("missing_fields", []),
    )
