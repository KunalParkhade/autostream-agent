from __future__ import annotations

from copy import deepcopy
from typing import Dict

from src.graph import build_graph
from src.state import AgentState, init_state


class AgentService:
    def __init__(self) -> None:
        self.graph = build_graph()
        self.sessions: Dict[str, AgentState] = {}

    def _get_or_create(self, session_id: str) -> AgentState:
        if session_id not in self.sessions:
            self.sessions[session_id] = init_state(session_id)
        return deepcopy(self.sessions[session_id])

    def chat(self, session_id: str, text: str) -> AgentState:
        state = self._get_or_create(session_id)
        state["user_input"] = text
        history = state.get("messages", [])
        history.append({"role": "user", "content": text})
        state["messages"] = history

        result = self.graph.invoke(state)

        result_history = result.get("messages", [])
        result_history.append({"role": "assistant", "content": result.get("response", "")})
        result["messages"] = result_history

        self.sessions[session_id] = deepcopy(result)
        return result


service = AgentService()
