"""Strategist agent for high-level strategic planning."""

from typing import TYPE_CHECKING
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from ..prompt import STRATEGIST_PROMPT

if TYPE_CHECKING:
    from langchain_openai import ChatOpenAI


class Strategist:
    """Strategist agent for formulating strategic objectives."""
    
    def __init__(self, model: "ChatOpenAI"):
        """Initialize strategist agent.
        
        Args:
            model: ChatOpenAI model instance
        """
        self.agent = create_agent(
            model,
            tools=[],
            system_prompt=STRATEGIST_PROMPT,
            response_format=None
        )
    
    def invoke(self, message: str) -> str:
        """Execute strategist agent and return strategic objective.
        
        Args:
            message: Context message with findings and target info
            
        Returns:
            Strategic objective as string
        """
        # LangGraph API uses messages list
        result = self.agent.invoke({
            "messages": [HumanMessage(content=message)]
        })
        # Extract last message content from LangGraph result
        messages = result.get("messages", [])
        if messages:
            last_message = messages[-1]
            return str(last_message.content)
        return ""

