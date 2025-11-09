"""Pathfinder agent for high-level strategic planning."""

from typing import Optional

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langgraph.store.base import BaseStore

from src.memory.context import memory_context
from src.scout.agents.base import BaseAgent
from src.scout.prompt import PATHFINDER_PROMPT
from src.scout.state import ScoutState
from src.scout.utils.message import MessageBuilder


class Pathfinder(BaseAgent):
    """Pathfinder agent for formulating strategic objectives."""

    def __init__(self) -> None:
        super().__init__()
        self.agent = create_agent(
            self.model,
            tools=[],
            system_prompt=PATHFINDER_PROMPT,
            response_format=None,
        )

    def invoke(self, state: ScoutState, store: Optional[BaseStore] = None) -> dict:
        with memory_context(store, state):
            result = self.agent.invoke(
                {
                    "messages": [
                        HumanMessage(content=MessageBuilder.build_pathfinder_message(state))
                    ]
                }
            )
        # Convert state to dict for merging
        state_dict = state.model_dump() if hasattr(state, 'model_dump') else dict(state)
        return {
            **state_dict,
            "messages": state.messages + result.get("messages", []),
            "objective": result.get("messages", [])[-1].content # TODO: think if necessary to ResponseFormat it, since redundant
        }

