from typing import TypedDict, Literal
from langchain_core.messages import AnyMessage

class GraphNode:
    """Graph node identifiers for agent routing."""
    RECON = "recon"
    SCOUT = "scout"
    END = "__end__"

GraphNodeType = Literal["recon", "scout", "__end__"]

class Finding(TypedDict):
    type: str
    description: str
    severity: str
    confidence: str
    metadata: dict

class FindingWithFeedback(Finding):
    feedback: str

class Target(TypedDict):
    ip: str
    port: int

class State(TypedDict):
    messages: list[AnyMessage]
    target: Target
    findings: list[FindingWithFeedback]