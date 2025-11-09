"""Routing logic for Scout agent to determine next graph node."""

from typing import TYPE_CHECKING, List
from src.state import State, GraphNode, GraphNodeType, Finding
from ..analysis import FlagDetector, SurfaceAnalyzer
import re

if TYPE_CHECKING:
    from langchain_openai import ChatOpenAI


class Router:
    """Determines the next agent after scout execution."""
    
    def __init__(self, model: "ChatOpenAI"):
        """Initialize router with analyzers.
        
        Args:
            model: ChatOpenAI model instance for surface analysis
        """
        self.flag_detector = FlagDetector()
        self.surface_analyzer = SurfaceAnalyzer(model)
    
    def route(self, state: State) -> GraphNodeType:
        """Determine next agent after scout execution.
        
        Args:
            state: Current state with findings
            
        Returns:
            Next graph node to visit (RECON, END)
        """
        # Get only scout-generated findings (most recent ones)
        all_findings = state.get("findings", [])
        if not all_findings:
            return GraphNode.RECON  # No findings, fallback to recon
        
        scout_findings = [f for f in all_findings if f.get("type", "").startswith("scout_")]
        
        # If no scout findings, something went wrong, go back to recon
        if not scout_findings:
            return GraphNode.RECON
        
        # Check most recent scout findings (last execution cycle)
        recent_scout_findings = scout_findings[-5:] if len(scout_findings) > 5 else scout_findings
        
        # Priority 1: Check if flag found
        for finding in recent_scout_findings:
            text = finding.get("description", "") + str(finding.get("metadata", {}))
            if self.flag_detector.detect(text):
                flags = self.flag_detector.extract_flags(text)
                # Only accept flags that exactly match flag{...} or FLAG{...}
                valid_flags = [f for f in (flags or []) if re.fullmatch(r'(?:flag|FLAG)\{[^}]+\}', f)]
                if valid_flags:
                    print("FLAG:", ", ".join(valid_flags))
                    # Attach flags to state so they are available at END
                    try:
                        findings_list = state.get("findings", [])
                        findings_list.append({
                            "type": "flag",
                            "description": f"Captured flags: {', '.join(valid_flags)}",
                            "severity": "high",
                            "confidence": "high",
                            "metadata": {
                                "flags": valid_flags,
                                "source": "router_detection"
                            },
                            "feedback": ""
                        })
                        state["findings"] = findings_list
                    except Exception:
                        # Best-effort: don't block graph termination on state mutation issues
                        pass
                    return GraphNode.END
        
        # Priority 2: Use LLM to analyze if new attack surface discovered
        new_surfaces = self.surface_analyzer.analyze_for_new_attack_surface(recent_scout_findings)
        
        if new_surfaces:
            # Store new attack surface information in state for recon agent to use
            # Add metadata to the original findings that were identified as new surfaces
            for surface_info in new_surfaces:
                finding_idx = surface_info.get("finding_id", -1)
                if 0 <= finding_idx < len(recent_scout_findings):
                    # Get the actual finding
                    actual_finding = recent_scout_findings[finding_idx]
                    
                    # Update the finding's metadata with new surface information
                    if "metadata" not in actual_finding:
                        actual_finding["metadata"] = {}
                    
                    actual_finding["metadata"]["new_attack_surface"] = {
                        "surface_type": surface_info.get("surface_type", "unknown"),
                        "description": surface_info.get("description", ""),
                        "priority": surface_info.get("priority", "medium"),
                        "requires_recon": True
                    }
            
            return GraphNode.RECON  # New attack surface found, go back to recon
        
        # Priority 3: Check severity - if high severity findings, may need more recon
        high_severity_count = sum(1 for f in recent_scout_findings if f.get("severity") == "high")
        
        # If multiple high-severity findings but no flag, might need more reconnaissance
        if high_severity_count > 0:
            return GraphNode.RECON  # Go back to enumerate new vectors based on what we learned
        
        # Default: End if we've exhausted the current attack vector
        # Return to scout to try again
        print("ENDING SCOUT")
        return GraphNode.SCOUT

