# AutoStream Social-to-Lead Agent

AutoStream is a fictional SaaS product for automated video editing. This repository contains an conversational agent that can identify intent, answer from a local knowledge base using RAG, and capture high-intent leads with guarded tool execution.

## Features

- Intent classification into:
	- casual greeting
	- product or pricing inquiry
	- high-intent lead
- Local knowledge base retrieval for pricing/features/policies
- Guarded lead capture tool invocation only after required fields are collected
- Multi-turn state retention with LangGraph
- Both CLI and FastAPI interfaces

The system uses FAISS-based vector retrieval instead of prompt injection to ensure scalable and production-grade RAG.

## Knowledge Base

The local knowledge base is stored in `data/knowledge_base.md` and includes:

- Basic Plan: $29/month, 10 videos/month, 720p
- Pro Plan: $79/month, unlimited videos, 4K, AI captions
- Policies: no refunds after 7 days, 24/7 support only on Pro

## Tech Stack

- Python 3.9+
- LangGraph + LangChain
- Gemini 2.5 Flash (`langchain-google-genai`)
- FAISS (`faiss-cpu`) for local vector retrieval
- FastAPI for HTTP endpoint

## Setup

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Configure environment variables:

```bash
cp .env.example .env
```

3. Set `GOOGLE_API_KEY` in `.env`.

## Run

### CLI

```bash
python -m src.cli
```

### FastAPI

```bash
uvicorn src.api:app --reload
```

Example request:

```bash
curl -X POST http://127.0.0.1:8000/chat \
	-H "Content-Type: application/json" \
	-d '{"session_id":"demo-1","message":"Hi, tell me about your pricing"}'
```

## Expected Flow

1. User asks pricing question -> RAG retrieves from local KB and answers.
2. User shows high intent (for example: "I want to sign up") -> lead flow starts.
3. Agent collects `name`, `email`, and `platform`.
4. Tool executes once all values are present and valid.

Safety guards:

- Tool is not called if required fields are missing.
- Tool is not called again if `lead_captured` is already `True`.

Captured leads are appended to `data/leads.json` as structured entries:

```json
{
	"name": "Kunal",
	"email": "kunal@email.com",
	"platform": "YouTube",
	"timestamp": "2026-04-12T10:30:00+00:00",
	"session_id": "demo-1"
}
```

## Architecture (Why LangGraph and How State Is Managed)

LangGraph is used because this workflow is explicitly stateful and conditional. A simple chat loop is not enough when behavior must switch between greeting handling, RAG retrieval, slot-filling for lead details, and guarded tool execution. The graph defines deterministic transitions: classify intent first, then route to either knowledge retrieval or lead collection paths. This makes branching logic transparent, testable, and easy to debug during interviews.

State is stored as a typed dictionary that includes conversation messages, current intent, captured lead fields (`name`, `email`, `platform`), missing fields, and a `lead_captured` boolean guard. For FastAPI, session continuity is maintained with `session_id` and an in-memory `sessions = {}` mapping in the shared service layer. This allows memory to persist across 5-6 turns per user session, while remaining simple for local assignment demos. Because the service is shared by CLI and API, both interfaces have identical core behavior and safety guarantees.

## WhatsApp Webhook Integration (Design)

To integrate this agent with WhatsApp in production:

1. Configure a webhook endpoint (for example, `/webhooks/whatsapp`) in FastAPI.
2. On inbound WhatsApp messages, extract sender phone number and map it to `session_id`.
3. Forward the message into the same agent service used by `/chat`.
4. Return the agent response via WhatsApp Cloud API outbound message endpoint.
5. Persist session state in Redis or a database (instead of in-memory dict) for horizontal scaling.
6. Add signature verification, retry handling, and observability for reliability.

This keeps channel integration thin while preserving the same LangGraph business logic.

## Tests

Run tests with:

```bash
pytest -q
```

The suite covers deterministic intent behavior, validation helpers, state initialization, and API smoke flow.
