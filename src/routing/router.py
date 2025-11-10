"""Routing logic for Scout agent to determine next graph node."""

from typing import Literal
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END
from langgraph.types import Command

from src.scout.state import ScoutState
from src.scout.agents.base import BaseAgent
from src.state import RedirectionModel, RedirectionWithSrc
from src.tool import get_hint, submit_answer

SYSTEM = """
You're a redirection LLM, you determine where does the execution go next.
* recon: reconnaissance agent for information gathering
* scout: scout agent for exploitation from given information context
* end: end the execution
                
You should return the following fields:
* dst: The destination node of the which node to redirect to.
* insight: The insight for the redirection.
(At the meantime, what you observed from the third-party, "god's view", e.g., what did the previous researcher missed that's maybe obvious to you?...)

Decide which agent should be pass to next
** If you find that previous agents are already able to find the flag, you should submit the flag via tool immediately.**
"""

class Router(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent = create_agent(
            self.model,
            tools=[submit_answer],
            system_prompt=SYSTEM,
            response_format=RedirectionModel,
        )

    def route(self, state: ScoutState) -> Command[Literal["recon", "scout", END]]:
        result = self.agent.invoke(
            {
                "messages": [HumanMessage(content=f"current state: {state}")]
            }
        )
        result = result.get("structured_response")
        
        if result.dst == "end":
            print(f"**MEOW: flag found: {result.insight}**")
            # Clone the existing list and append the new entry
            redirection_list = state.get("redirection", [])[:] # Create a copy
            redirection_list.append(
                RedirectionWithSrc(
                    dst="end",
                    insight=result.insight,
                    src="router"
                )
            )
            return Command(
                goto=END,
                update={
                    "flag": result.insight,
                    "redirection": redirection_list
                }
            )
        
        elif result.dst == "recon":
            # Clone the existing list and append the new entry
            redirection_list = state.get("redirection", [])[:] # Create a copy
            redirection_list.append(
                RedirectionWithSrc(
                    dst="recon",
                    insight=result.insight,
                    src="router"
                )
            )
            return Command(
                goto="recon",
                update={
                    "messages": state.get("messages", []) + [HumanMessage(content=f"Router insight: {result.insight}")],
                    "redirection": redirection_list
                }
            )
            
        elif result.dst == "scout":
            # Clone the existing list and append the new entry
            redirection_list = state.get("redirection", [])[:] # Create a copy
            redirection_list.append(
                RedirectionWithSrc(
                    dst="scout",
                    insight=result.insight,
                    src="router"
                )
            )
            return Command(
                goto="scout",
                update={
                    "messages": state.get("messages", []) + [HumanMessage(content=f"Router insight: {result.insight}")],
                    "redirection": redirection_list
                }
            )

    # """Determines the next agent after scout execution."""

    # def __init__(self, model: "ChatOpenAI"):
    #     """Initialize router with analyzers.

    #     Args:
    #         model: ChatOpenAI model instance for surface analysis
    #     """
    #     self.flag_detector = FlagDetector()
    #     self.surface_analyzer = SurfaceAnalyzer(model)

    # def route(self, state: State) -> GraphNodeType:
    #     """Determine next agent after scout execution.

    #     Args:
    #         state: Current state with findings

    #     Returns:
    #         Next graph node to visit (RECON, END)
    #     """
    #     # Get only scout-generated findings (most recent ones)
    #     all_findings = state.get("findings", [])
    #     if not all_findings:
    #         return GraphNode.RECON  # No findings, fallback to recon

    #     scout_findings = [f for f in all_findings if f.get("type", "").startswith("scout_")]

    #     # If no scout findings, something went wrong, go back to recon
    #     if not scout_findings:
    #         return GraphNode.RECON

    #     # Check most recent scout findings (last execution cycle)
    #     recent_scout_findings = scout_findings[-5:] if len(scout_findings) > 5 else scout_findings

    #     # Priority 1: Check if flag found
    #     for finding in recent_scout_findings:
    #         text = finding.get("description", "") + str(finding.get("metadata", {}))
    #         if self.flag_detector.detect(text):
    #             return GraphNode.END  # Flag found, mission complete

    #     # Priority 2: Use LLM to analyze if new attack surface discovered
    #     new_surfaces = self.surface_analyzer.analyze_for_new_attack_surface(recent_scout_findings)

    #     if new_surfaces:
    #         # Store new attack surface information in state for recon agent to use
    #         # Add metadata to the original findings that were identified as new surfaces
    #         for surface_info in new_surfaces:
    #             finding_idx = surface_info.get("finding_id", -1)
    #             if 0 <= finding_idx < len(recent_scout_findings):
    #                 # Get the actual finding
    #                 actual_finding = recent_scout_findings[finding_idx]

    #                 # Update the finding's metadata with new surface information
    #                 if "metadata" not in actual_finding:
    #                     actual_finding["metadata"] = {}

    #                 actual_finding["metadata"]["new_attack_surface"] = {
    #                     "surface_type": surface_info.get("surface_type", "unknown"),
    #                     "description": surface_info.get("description", ""),
    #                     "priority": surface_info.get("priority", "medium"),
    #                     "requires_recon": True
    #                 }

    #         return GraphNode.RECON  # New attack surface found, go back to recon

    #     # Priority 3: Check severity - if high severity findings, may need more recon
    #     high_severity_count = sum(1 for f in recent_scout_findings if f.get("severity") == "high")

    #     # If multiple high-severity findings but no flag, might need more reconnaissance
    #     if high_severity_count > 0:
    #         return GraphNode.RECON  # Go back to enumerate new vectors based on what we learned

    #     # Default: End if we've exhausted the current attack vector
    #     # Avoid infinite scout loops
    #     return GraphNode.END
