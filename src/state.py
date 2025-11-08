from typing import Any, List, Literal, TypedDict

from langchain_core.messages import AnyMessage
from pydantic import BaseModel


class GraphNode:
    """Graph node identifiers for agent routing."""

    RECON = "recon"
    SCOUT = "scout"
    END = "__end__"


GraphNodeType = Literal["recon", "scout", "__end__"]


# Pydantic Models
class FindingModel(BaseModel):
    type: str
    description: str
    severity: str
    confidence: str
    metadata: dict[str, Any]

    def to_struct(self) -> dict[str, Any]:
        """Convert to TypedDict-compatible dictionary."""
        return {
            "type": self.type,
            "description": self.description,
            "severity": self.severity,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


class FindingWithFeedbackModel(FindingModel):
    feedback: str

    def to_struct(self) -> dict[str, Any]:
        """Convert to TypedDict-compatible dictionary."""
        base = super().to_struct()
        base["feedback"] = self.feedback
        return base


class TargetModel(BaseModel):
    ip: str
    port: int

    def to_struct(self) -> dict[str, Any]:
        """Convert to TypedDict-compatible dictionary."""
        return {
            "ip": self.ip,
            "port": self.port,
        }


class StateModel(BaseModel):
    messages: list[AnyMessage]
    target: TargetModel
    findings: list[FindingWithFeedbackModel]

    def to_struct(self) -> dict[str, Any]:
        """Convert to TypedDict-compatible dictionary."""
        return {
            "messages": self.messages,
            "target": self.target.to_struct(),
            "findings": [finding.to_struct() for finding in self.findings],
        }


class ListFindingsWithFeedbackModel(BaseModel):
    findings: List[FindingWithFeedbackModel]

    def to_struct(self) -> dict[str, Any]:
        """Convert to TypedDict-compatible dictionary."""
        return {
            "findings": [finding.to_struct() for finding in self.findings],
        }


# TypedDict versions (original names)
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
