from typing import TypedDict

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
    target: Target
    findings: list[FindingWithFeedback]