from typing import TypedDict
from langchain_core.messages import AnyMessage

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