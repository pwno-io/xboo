"""Executor agent for script generation and task execution."""

from typing import TYPE_CHECKING
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from ..prompt import EXECUTOR_PROMPT
from ..tools import execution, python
from langchain_openai import ChatOpenAI


class Executor:
    """Executor agent for executing tasks with tools."""
    
    def __init__(self, model: "ChatOpenAI"):
        """Initialize executor agent.
        
        Args:
            model: ChatOpenAI model instance
        """
        self.agent = create_agent(
            model,
            tools=[execution, python],
            system_prompt=EXECUTOR_PROMPT,
            response_format=None
        )
    
    def invoke(self, message: str) -> str:
        """Execute task using ReAct agent with tools.
        
        Args:
            message: Context message with task details
            
        Returns:
            Execution output as string
        """
        try:
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
            
        except Exception as e:
            return f"Error during execution: {str(e)}"

