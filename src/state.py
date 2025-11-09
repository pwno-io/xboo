import json
from typing import Any, Dict, List, Literal, NotRequired, Optional, TypedDict

from langchain_core.messages import AnyMessage
from pydantic import BaseModel, Field


# Pydantic Models
class FindingModel(BaseModel):
    type: Literal["information", "curiosity", "vulnerability"] = Field(
        description="The type of the finding."
    )
    description: str = Field(description="The description of the finding.")
    confidence: float = Field(description="The confidence of the finding.")
    metadata_json: str = Field(description="The metadata of the finding.")


class FindingWithFeedbackModel(FindingModel):
    feedback: str


class TargetModel(BaseModel):
    ip: str
    port: int
    annotation: str = Field(description="What is the target?")


class StateModel(BaseModel):
    messages: list[AnyMessage] = Field(default_factory=list)
    target: List[TargetModel] = Field(default_factory=list)
    findings: list[FindingWithFeedbackModel] = Field(default_factory=list)


class ReconOutput(BaseModel):
    report: str = Field(description="The report of the reconnaissance.")
    findings: List[FindingWithFeedbackModel]
    target: List[TargetModel]  # why do we need


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


# FOR conditional edges
class Redirection(TypedDict):
    # src: str # this would be hard-override by current node
    dst: Literal["recon", "scout", "end"] = Field(
        description="The destination node of the which node to redirect to."
    )
    reason: str = Field(description="The reason for the redirection.")

class RedirectionWithSrc(Redirection):
    src: Literal["recon", "scout", "end"] = Field(
        description="The source node of the which node to redirect from."
    )
class RedirectionModel(BaseModel):
    dst: Literal["recon", "scout", "end"] = Field(
        description="The destination node of the which node to redirect to."
    )
    insight: str = Field(description="The insight for the redirection.")


class State(TypedDict):
    messages: list[AnyMessage]

    target: list[Target]
    recon: str

    findings: list[FindingWithFeedback]
    flag: str = Field(description="The flag of the challenge.")
    redirection: list[RedirectionWithSrc] = Field(default_factory=list)
    # plan: NotRequired[Dict[str, Any]]
    # memory: NotRequired[List[Dict[str, Any]]]
