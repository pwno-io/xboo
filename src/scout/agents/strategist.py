"""Strategist agent for high-level strategic planning."""

from langchain_core.messages import HumanMessage
from langchain.agents import create_agent

from src.scout.utils.message import MessageBuilder
from src.scout.agents.base import BaseAgent
from src.scout.prompt import STRATEGIST_PROMPT
from src.scout.state import ScoutState
class Strategist(BaseAgent):
    """Strategist agent for formulating strategic objectives."""
    
    def __init__(self):
        super().__init__()
        self.agent = create_agent(
            self.model,
            tools=[],
            system_prompt=STRATEGIST_PROMPT,
            response_format=None
        )
    
    def invoke(self, state: ScoutState) -> ScoutState:
        result = self.agent.invoke(
            {
                "messages": [
                    HumanMessage(content=MessageBuilder.build_strategist_message(state))
                ]
            }
        )
        return {
            **state,
            "messages": state.get("messages", []) + result.get("messages", []),
            "objective": result.get("messages", [])[-1].content # TODO: think if necessary to ResponseFormat it, since redundant
        }

