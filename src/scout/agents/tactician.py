"""Tactician agent for task breakdown and DAG creation."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional, Tuple

import networkx as nx
from networkx.readwrite import json_graph
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from pydantic import ValidationError

from src.scout.state import ScoutState
from src.scout.utils.message import MessageBuilder
from src.scout.agents.base import BaseAgent
from src.scout.model import ResponseGraph
from src.scout.prompt import TACTICIAN_PROMPT


class Tactician(BaseAgent):
    
    def __init__(self):
        super().__init__()
        self.agent = create_agent(
            self.model,
            system_prompt=TACTICIAN_PROMPT,
            response_format=ResponseGraph,
        )

    def invoke(self, state: ScoutState) -> ScoutState:
        """Execute tactician agent and return serialized DAG state payload."""
        result = self.agent.invoke(
            {
                "messages": [
                    HumanMessage(content=MessageBuilder.build_tactician_message(state))
                    ]
                }
            )