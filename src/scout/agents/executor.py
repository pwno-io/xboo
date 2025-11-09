"""Executor agent for script generation and task execution."""

from typing import Any, Optional

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langgraph.store.base import BaseStore

from src.memory.context import memory_context
from src.scout.utils.message import MessageBuilder

from ..prompt import EXECUTOR_PROMPT
from src.tool import memory_log, run_bash, run_ipython
from src.scout.agents.base import BaseAgent
from src.scout.state import ScoutState
from src.state import State


class Executor(BaseAgent):
    """Executor agent for executing tasks with tools."""

    def __init__(self):
        super().__init__()
        self.agent = create_agent(
            self.model,
            tools=[run_bash, run_ipython, memory_log],
            system_prompt=EXECUTOR_PROMPT,
            response_format=None
        )

    # NOTE: executor should return a state type of parent graph
    def invoke(self, state: ScoutState, store: Optional[BaseStore] = None) -> dict:
        try:
            with memory_context(store, state):
                result = self.agent.invoke(
                    {
                        "messages": [HumanMessage(content=MessageBuilder.build_executor_message(state))]
                    }
                )
            # Convert state to dict for merging
            state_dict = state.model_dump() if hasattr(state, 'model_dump') else dict(state)
            return {**state_dict, "messages": state.messages + result.get("messages", [])}
        except Exception as e:  # pylint: disable=broad-except
            # Always return a dict to satisfy LangGraph's state update contract
            state_dict = state.model_dump() if hasattr(state, 'model_dump') else dict[str, Any](state)
            error_message = HumanMessage(content=f"Error during execution: {str(e)}")
            return {**state_dict, "messages": state.messages + [error_message]}

