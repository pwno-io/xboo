"""Pydantic schemas for task DAG used by the Tactician stage."""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class DagNode(BaseModel):
    """A node in the task DAG."""

    id: str
    phase: Literal["enumerate", "trigger", "observe", "compare"]
    description: str
    # Optional, still supported for backward compatibility
    dependencies: List[str] = Field(default_factory=list)


class DagEdge(BaseModel):
    """A directed edge in the task DAG linking two nodes by id."""

    source: str  # upstream node id
    target: str  # downstream node id


class TaskDag(BaseModel):
    """Complete DAG with nodes, edges, and evidence criteria."""

    nodes: List[DagNode]
    edges: List[DagEdge] = Field(default_factory=list)
    evidence_criteria: str


