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

        if (graph := self._extract_response_graph(result)) is None:
            raise ValueError("No response graph found")

        task_graph, dag = self._build_graph_outputs(graph)
        dag_payload = json_graph.node_link_data(dag)

        try:
            topological_order = list(nx.topological_sort(dag))
        except nx.NetworkXUnfeasible:
            topological_order = [node["id"] for node in task_graph.get("nodes", [])]

        return {
            **state,
            "messages": state.get("messages", []) + result.get("messages", []),
            "DAG": {
                "task_graph": task_graph,
                "dag": dag_payload,
                "topological_order": topological_order,
            }
        }


    def _extract_response_graph(self, result: Dict[str, Any]) -> Optional[ResponseGraph]:
        """Find the first ResponseGraph payload within the agent execution result."""
        candidates = [
            result.get("response"),
            result.get("output"),
            result.get("response_graph"),
        ]

        for candidate in candidates:
            graph = self._coerce_response_graph(candidate)
            if graph is not None:
                return graph

        for message in reversed(result.get("messages", [])):
            graph = self._coerce_response_graph(getattr(message, "content", None))
            if graph is not None:
                return graph

            for tool_call in getattr(message, "tool_calls", []) or []:
                graph = self._coerce_response_graph(tool_call.get("args"))
                if graph is not None:
                    return graph

        return None

    def _coerce_response_graph(self, payload: Any) -> Optional[ResponseGraph]:
        """Attempt to coerce an arbitrary payload into a ResponseGraph instance."""
        if payload is None:
            return None

        if isinstance(payload, ResponseGraph):
            return payload

        if hasattr(payload, "model_dump"):
            return self._coerce_response_graph(payload.model_dump())

        if isinstance(payload, str):
            try:
                parsed = json.loads(payload)
            except (TypeError, json.JSONDecodeError):
                return None
            return self._coerce_response_graph(parsed)

        if isinstance(payload, dict):
            normalized = self._normalize_payload(payload)
            if normalized is None:
                return None
            try:
                return ResponseGraph.model_validate(normalized)
            except ValidationError:
                return None

        return None

    def _normalize_payload(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normalize heterogeneous payload keys to ResponseGraph schema."""
        if "nodes" not in payload:
            return None

        normalized: Dict[str, Any] = dict(payload)

        if "annotation" not in normalized and "evidence_criteria" in normalized:
            normalized["annotation"] = normalized.pop("evidence_criteria")

        edges = []
        for edge in normalized.get("edges", []) or []:
            src = edge.get("src") or edge.get("source")
            dst = edge.get("dst") or edge.get("target")
            if not (src and dst):
                continue
            edges.append({"src": src, "dst": dst})
        normalized["edges"] = edges

        nodes = []
        for node in normalized.get("nodes", []) or []:
            node_id = node.get("id")
            phase = node.get("phase")
            description = node.get("description")
            if not (node_id and phase and description):
                continue
            nodes.append(
                {
                    "id": node_id,
                    "phase": phase,
                    "description": description,
                    "dependencies": node.get("dependencies", []),
                }
            )
        normalized["nodes"] = nodes

        return normalized

    def _build_graph_outputs(
        self, response: ResponseGraph
    ) -> Tuple[Dict[str, Any], nx.DiGraph]:
        """Convert ResponseGraph into task graph dict and networkx DAG."""
        dag = nx.DiGraph()

        nodes = []
        for node in response.nodes:
            node_dict = node.model_dump()
            nodes.append(node_dict)
            dag.add_node(node.id, phase=node.phase, description=node.description)

        edges = []
        for edge in response.edges:
            dag.add_edge(edge.src, edge.dst)
            edges.append({"source": edge.src, "target": edge.dst})

        if not edges:
            for node in response.nodes:
                for dependency in node.dependencies:
                    dag.add_edge(dependency, node.id)
                    edges.append({"source": dependency, "target": node.id})

        task_graph: Dict[str, Any] = {
            "nodes": nodes,
            "edges": edges,
            "evidence_criteria": response.annotation,
        }

        return task_graph, dag