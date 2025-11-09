from typing import Any, Dict
from pydantic import Field

from src.state import StateModel


class ScoutState(StateModel):
    objective: str = Field(description="The strategic objective for the scout agent.", default="")
    DAG: Dict[str, Any] = Field(
        default_factory=dict,
        description="Serialized task graph payload containing node-link DAG data.",
    )
