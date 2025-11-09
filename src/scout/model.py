# - Schema summary:
#   - Node: { id: string, phase: enumerate|trigger|observe|compare, description: string, dependencies?: string[] }
#   - Edge: { source: string, target: string }
#   - TaskDag fields: nodes: Node[], edges: Edge[], evidence_criteria: string

from typing import Literal, List
from pydantic import BaseModel, Field

class DagNode(BaseModel):
  id: str
  phase: Literal["enumerate", "trigger", "observe", "compare"]
  description: str
  dependencies: List[str] = Field(default_factory=list)

class DagEdge(BaseModel):
  src: str
  dst: str

class ResponseGraph(BaseModel):
  nodes: List[DagNode]
  edges: List[DagEdge]
  annotation: str = Field(description="Evidence criteria")