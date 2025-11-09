# Plan and memory schema definitions for scout agents.

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class PlanPhase(BaseModel):
    id: int = Field(description="Sequential identifier for this phase.")
    title: str = Field(description="Concise name describing the focus of the phase.")
    status: Literal["pending", "active", "done", "blocked", "partial_failure"] = Field(
        default="pending",
        description="Current completion status for the phase.",
    )
    criteria: str = Field(description="Measurable exit criteria for the phase.")
    notes: Optional[str] = Field(
        default=None,
        description="Operational notes or observations that inform execution.",
    )


class PlanModel(BaseModel):
    objective: str = Field(description="The strategic objective this plan addresses.")
    current_phase: int = Field(
        description="Numeric pointer to the active phase (1-indexed)."
    )
    total_phases: int = Field(description="Total number of phases in the plan.")
    phases: List[PlanPhase] = Field(
        description="Ordered list of phases required to complete the objective."
    )
    summary: Optional[str] = Field(
        default=None,
        description="Optional one paragraph summary of the overall plan.",
    )


class MemoryUpdate(BaseModel):
    category: Literal["plan", "finding", "reflection", "note"] = Field(
        description="Memory entry category for downstream processing."
    )
    content: str = Field(description="Content to persist in memory storage.")
    metadata: Dict[str, str] = Field(
        default_factory=dict,
        description="Lightweight metadata describing the memory entry.",
    )


class PlanResponse(BaseModel):
    plan: PlanModel
    memory: List[MemoryUpdate] = Field(
        default_factory=list,
        description="Memory updates accompanying the plan.",
    )