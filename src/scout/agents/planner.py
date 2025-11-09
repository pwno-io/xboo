"""Planner agent responsible for building plan and memory updates."""

from __future__ import annotations

from typing import List, Optional

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langgraph.store.base import BaseStore
from pydantic import ValidationError

from src.memory.context import memory_context
from src.scout.agents.base import BaseAgent
from src.scout.model import PlanResponse
from src.scout.prompt import PLANNER_PROMPT
from src.scout.state import ScoutState
from src.scout.utils.message import MessageBuilder
from src.tool import store_plan_to_memory


class Planner(BaseAgent):
    def __init__(self) -> None:
        super().__init__()
        self.agent = create_agent(
            self.model,
            system_prompt=PLANNER_PROMPT,
            response_format=PlanResponse,
        )

    def invoke(self, state: ScoutState, store: Optional[BaseStore] = None) -> ScoutState:
        """Execute planner agent and return plan + memory aware state."""
        with memory_context(store, state):
            try:
                result = self.agent.invoke(
                    {
                        "messages": [
                            HumanMessage(
                                content=MessageBuilder.build_planner_message(state)
                            )
                        ]
                    }
                )
            except ValidationError as exc:
                raise ValueError(f"Planner response failed validation: {exc}") from exc

        structured = result.get("structured_response")
        if structured is None:
            raise ValueError("Planner did not return a structured PlanResponse.")

        plan_payload = structured.plan.model_dump()
        memory_payload: List[dict] = [entry.model_dump() for entry in structured.memory]

        # Ensure the plan carries the latest objective context
        if not plan_payload.get("objective"):
            plan_payload["objective"] = state.get("objective", "")

        try:
            store_plan_to_memory(plan_payload, state)
        except ValueError:
            # Gracefully degrade if persistence fails (e.g., invalid payload)
            pass

        updated_memory = state.get("memory", []) + memory_payload

        return {
            **state,
            "messages": state.get("messages", []) + result.get("messages", []),
            "plan": plan_payload,
            "memory": updated_memory,
        }