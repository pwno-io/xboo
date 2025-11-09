"""Message construction utilities for Scout agents."""

from src.scout.state import ScoutState
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
    def build_tactician_message(state: ScoutState) -> str:
        """Build context message for tactician agent.

        Args:
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

        return f"""STRATEGIC OBJECTIVE: {state.get("objective")}
CURRENT STATE:
Target(s): {target_str}
Known Findings: {findings_summary if findings_summary else "No findings yet"}

Create a task DAG to accomplish this strategic objective.
"""

    @staticmethod
    def build_executor_message(state: ScoutState) -> str:
        """Build context message for executor agent.

        Args:
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

        return f"""STRATEGIC OBJECTIVE: {state.get("objective")}

CURRENT TASK DAG:
{state.get("DAG", {})}

TARGET(S): {target_str}

Execute this task using available tools."""
