"""Tactician agent for task breakdown and DAG creation."""

from typing import TYPE_CHECKING, Tuple, Dict
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from ..prompt import TACTICIAN_PROMPT
from ..tools import create_task_dag
import json
import networkx as nx

if TYPE_CHECKING:
    from langchain_openai import ChatOpenAI


class Tactician:
    """Tactician agent for creating task DAGs."""
    
    def __init__(self, model: "ChatOpenAI"):
        """Initialize tactician agent.
        
        Args:
            model: ChatOpenAI model instance
        """
        self.agent = create_agent(
            model,
            tools=[create_task_dag],
            system_prompt=TACTICIAN_PROMPT,
            response_format=None
        )
    
    def invoke(self, message: str) -> Tuple[Dict, nx.DiGraph]:
        """Execute tactician agent and return task graph.
        
        Args:
            message: Context message with strategic objective
            
        Returns:
            Tuple of (task_graph dict, NetworkX DiGraph)
        """
        # LangGraph API uses messages list
        result = self.agent.invoke({
            "messages": [HumanMessage(content=message)]
        })
        
        # Extract last message content from LangGraph result
        messages = result.get("messages", [])
        tactician_output = ""
        if messages:
            last_message = messages[-1]
            tactician_output = str(last_message.content)
        
        try:
            task_data = json.loads(tactician_output)

            # Build networkx DAG
            G = nx.DiGraph()

            # Add nodes
            for node in task_data.get("nodes", []):
                G.add_node(
                    node["id"],
                    phase=node.get("phase", ""),
                    description=node.get("description", "")
                )

            # Prefer explicit edges; fallback to per-node dependencies
            edges = task_data.get("edges", [])
            if edges:
                for edge in edges:
                    G.add_edge(edge["source"], edge["target"])
            else:
                for node in task_data.get("nodes", []):
                    for dep in node.get("dependencies", []):
                        G.add_edge(dep, node["id"])

            # Serialize for state storage
            task_graph = {
                "nodes": task_data.get("nodes", []),
                "edges": edges,
                "evidence_criteria": task_data.get("evidence_criteria", "")
            }

            return task_graph, G
            
        except (json.JSONDecodeError, KeyError) as e:
            # Fallback: create simple linear task graph
            task_graph = {
                "nodes": [
                    {"id": "task_1", "phase": "enumerate", "description": "Basic enumeration", "dependencies": []},
                    {"id": "task_2", "phase": "trigger", "description": "Execute test", "dependencies": ["task_1"]}
                ],
                "evidence_criteria": "Any successful response"
            }
            G = nx.DiGraph()
            G.add_edge("task_1", "task_2")
            
            return task_graph, G

