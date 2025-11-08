"""Structured tool for creating a task DAG via function call."""

import json
from langchain_core.tools import tool
from ..utils.schemas import TaskDag


@tool("create_task_dag", args_schema=TaskDag)
def create_task_dag(nodes, edges, evidence_criteria):  # type: ignore[no-untyped-def]
    """Return a validated task DAG. Use this tool to submit your DAG.

    Provide nodes, edges, and evidence_criteria that define an executable DAG.
    """
    dag = TaskDag(nodes=nodes, edges=edges, evidence_criteria=evidence_criteria)
    # Return as JSON string for downstream parsing
    return json.dumps(dag.model_dump())