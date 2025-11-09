"""Message construction utilities for Scout agents."""

from src.scout.state import ScoutState
from src.state import State


class MessageBuilder:
    """Builds context messages for Scout agents."""

    @staticmethod
    def _plan_to_lines(plan) -> list[str]:
        if not plan:
            return ["No active plan. Craft one now."]
        plan_dict = plan.model_dump() if hasattr(plan, "model_dump") else plan
        phases = plan_dict.get("phases", [])
        if not phases:
            return ["Plan exists but lacks phases. Provide measurable steps."]
        lines: list[str] = []
        for phase in phases:
            phase_dict = phase.model_dump() if hasattr(phase, "model_dump") else phase
            status = str(phase_dict.get("status", "pending")).upper()
            title = phase_dict.get("title", "Untitled phase")
            criteria = phase_dict.get("criteria", "Unspecified exit criteria")
            lines.append(f"- [{status}] {title} :: {criteria}")
        return lines

    @staticmethod
    def _memory_to_lines(memory) -> list[str]:
        if not memory:
            return ["No memory captured yet."]
        lines: list[str] = []
        tail = memory[-3:]
        for entry in tail:
            entry_dict = entry.model_dump() if hasattr(entry, "model_dump") else entry
            category = str(entry_dict.get("category", "note")).upper()
            content = entry_dict.get("content", "")
            metadata = entry_dict.get("metadata", {}) or {}
            meta_str = (
                f" | metadata: {metadata}" if metadata else ""
            )
            lines.append(f"- [{category}] {content}{meta_str}")
        return lines

    @staticmethod
    def build_pathfinder_message(state) -> str:
        """Build context message for the pathfinder agent."""
        # Handle both State (TypedDict) and ScoutState (Pydantic)
        if hasattr(state, 'findings'):
            # Pydantic model
            findings = state.findings
            targets = state.target
            memory = state.memory if hasattr(state, 'memory') else []
        else:
            # TypedDict
            findings = state.get("findings", [])
            targets = state.get("target", [])
            memory = state.get("memory", [])
        
        findings_summary = "\n".join(
            [
                f"- [{f.type if hasattr(f, 'type') else f['type']}] "
                f"{f.description if hasattr(f, 'description') else f['description']} "
                f"(Severity: {f.get('severity', 'N/A') if hasattr(f, 'get') else getattr(f, 'severity', 'N/A')}, "
                f"Confidence: {f.confidence if hasattr(f, 'confidence') else f['confidence']})"
                for f in findings
            ]
        )

        if targets:
            target_str = "\n".join(
                [f"  - {t.ip if hasattr(t, 'ip') else t.get('ip', 'Unknown')}:"
                 f"{t.port if hasattr(t, 'port') else t.get('port', 'Unknown')}" 
                 for t in targets]
            )
        else:
            target_str = "  No targets identified yet"

        memory_lines = MessageBuilder._memory_to_lines(memory)
        memory_summary = "\n".join(memory_lines)

        return f"""CONTEXT:
Target(s):
{target_str}

Reconnaissance Findings:
{findings_summary if findings_summary else 'No findings yet'}

Recent Memory Highlights:
{memory_summary}

Based on these signals, focus the objective on the most impactful path forward."""

    @staticmethod
    def build_planner_message(state: ScoutState) -> str:
        """Build context message for the planner agent."""
        findings = state.findings if hasattr(state, 'findings') else []
        findings_summary = "\n".join(
            [f"- [{f.type if hasattr(f, 'type') else f['type']}] {f.description if hasattr(f, 'description') else f['description']}" 
             for f in findings]
        )

        targets = state.target if hasattr(state, 'target') else []
        if targets:
            target_str = ", ".join(
                [f"{t.ip if hasattr(t, 'ip') else t.get('ip', 'Unknown')}:{t.port if hasattr(t, 'port') else t.get('port', 'Unknown')}" 
                 for t in targets]
            )
        else:
            target_str = "No targets identified yet"

        plan_lines = MessageBuilder._plan_to_lines(state.plan if hasattr(state, 'plan') else None)
        plan_summary = "\n".join(plan_lines)
        memory_lines = MessageBuilder._memory_to_lines(state.memory if hasattr(state, 'memory') else [])
        memory_summary = "\n".join(memory_lines)

        findings_text = findings_summary if findings_summary else "No findings yet"
        objective = state.objective if hasattr(state, 'objective') else 'Unspecified objective'

        return f"""STRATEGIC OBJECTIVE: {objective}
CURRENT TARGETS: {target_str}
KNOWN FINDINGS:
{findings_text}

CURRENT PLAN SNAPSHOT:
{plan_summary}

RECENT MEMORY HIGHLIGHTS:
{memory_summary}

Develop a refreshed multi-phase plan (1-4 phases) with clear exit criteria. Use the structured response format to provide:
- plan.current_phase
- plan.total_phases
- plan.phases[] with title, status, criteria, optional notes
- memory[] entries capturing critical insights or follow-up tasks.
"""

    @staticmethod
    def build_executor_message(state: ScoutState) -> str:
        """Build context message for executor agent."""
        targets = state.target if hasattr(state, 'target') else []
        if targets:
            target_str = ", ".join(
                [f"{t.ip if hasattr(t, 'ip') else t.get('ip', 'Unknown')}:{t.port if hasattr(t, 'port') else t.get('port', 'Unknown')}" 
                 for t in targets]
            )
        else:
            target_str = "No targets identified yet"

        plan_lines = MessageBuilder._plan_to_lines(state.plan if hasattr(state, 'plan') else None)
        plan_summary = "\n".join(plan_lines)
        memory_lines = MessageBuilder._memory_to_lines(state.memory if hasattr(state, 'memory') else [])
        memory_summary = "\n".join(memory_lines)
        
        objective = state.objective if hasattr(state, 'objective') else 'Unspecified objective'

        return f"""STRATEGIC OBJECTIVE: {objective}

ACTIVE PLAN:
{plan_summary}

RECENT MEMORY HIGHLIGHTS:
{memory_summary}

TARGET(S): {target_str}

Execute the next phase in the plan using the available tools. When generating evidence or insights, call the memory tool to persist entries.
"""
