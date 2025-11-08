"""Message construction utilities for Scout agents."""

from src.state import State
from typing import List


class MessageBuilder:
    """Builds context messages for Scout agents."""

    @staticmethod
    def build_strategist_message(state: State) -> str:
        """Build context message for strategist agent.

        Args:
            state: Current state with target and findings

        Returns:
            Formatted message for strategist
        """
        findings_summary = "\n".join(
            [
                f"- [{f['type']}] {f['description']} (Severity: {f['severity']}, Confidence: {f['confidence']})"
                for f in state.get("findings", [])
            ]
        )

        # Format target list
        targets = state.get("target", [])
        if targets:
            target_str = "\n".join(
                [f"  - {t.get('ip', 'Unknown')}:{t.get('port', 'Unknown')}" for t in targets]
            )
        else:
            target_str = "  No targets identified yet"

        return f"""CONTEXT:
Target(s):
{target_str}

Reconnaissance Findings:
{findings_summary if findings_summary else "No findings yet"}

Based on these findings, formulate a strategic objective for exploitation."""

    @staticmethod
    def build_tactician_message(strategic_objective: str, state: State) -> str:
        """Build context message for tactician agent.

        Args:
            strategic_objective: The strategic objective from strategist
            state: Current state with target and findings

        Returns:
            Formatted message for tactician
        """
        findings_summary = "\n".join(
            [f"- [{f['type']}] {f['description']}" for f in state.get("findings", [])]
        )

        # Format target list
        targets = state.get("target", [])
        if targets:
            target_str = ", ".join(
                [f"{t.get('ip', 'Unknown')}:{t.get('port', 'Unknown')}" for t in targets]
            )
        else:
            target_str = "No targets identified yet"

        return f"""STRATEGIC OBJECTIVE: {strategic_objective}

CURRENT STATE:
Target(s): {target_str}
Known Findings: {findings_summary if findings_summary else "No findings yet"}

Create a task DAG to accomplish this strategic objective.

Use the function call create_task_dag to submit the DAG. Define:
- Node: {{ id: string, phase: enumerate|trigger|observe|compare, description: string, dependencies?: string[] }}
- Edge: {{ source: string, target: string }}
Return ONLY the function call with fields: nodes, edges, evidence_criteria. Include 3-7 nodes."""

    @staticmethod
    def build_executor_message(task_node: dict, strategic_objective: str, state: State) -> str:
        """Build context message for executor agent.

        Args:
            task_node: Task node with id, phase, and description
            strategic_objective: The strategic objective from strategist
            state: Current state with target information

        Returns:
            Formatted message for executor
        """
        # Format target list
        targets = state.get("target", [])
        if targets:
            target_str = ", ".join(
                [f"{t.get('ip', 'Unknown')}:{t.get('port', 'Unknown')}" for t in targets]
            )
        else:
            target_str = "No targets identified yet"

        return f"""STRATEGIC OBJECTIVE: {strategic_objective}

CURRENT TASK:
- ID: {task_node["id"]}
- Phase: {task_node["phase"]}
- Description: {task_node["description"]}

TARGET(S): {target_str}

Execute this task using available tools."""
