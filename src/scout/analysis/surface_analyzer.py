"""Attack surface analysis for penetration testing."""

from typing import TYPE_CHECKING, List
from langchain_core.messages import HumanMessage
from src.state import Finding
import json

if TYPE_CHECKING:
    from langchain_openai import ChatOpenAI


class SurfaceAnalyzer:
    """Analyzes findings to identify new attack surfaces using LLM."""
    
    def __init__(self, model: "ChatOpenAI"):
        """Initialize surface analyzer with LLM model.
        
        Args:
            model: ChatOpenAI model instance for analysis
        """
        self.model = model
    
    def analyze_for_new_attack_surface(self, findings: List[Finding]) -> List[dict]:
        """Use LLM to analyze findings and identify new attack surfaces.
        
        Args:
            findings: List of findings to analyze
            
        Returns:
            List of analysis results for findings that represent new attack surfaces
        """
        if not findings:
            return []
        
        # Prepare findings summary for analysis
        findings_summary = []
        for finding in findings:
            findings_summary.append({
                "type": finding.get("type", ""),
                "description": finding.get("description", ""),
                "severity": finding.get("severity", ""),
                "metadata": finding.get("metadata", {})
            })
        
        # Build analysis prompt
        analysis_prompt = f"""Analyze the following findings from penetration testing to determine if they reveal NEW ATTACK SURFACES that require additional reconnaissance.

Findings to analyze:
{json.dumps(findings_summary, indent=2)}

For each finding, determine:
1. Does it reveal a NEW attack surface (new ports, services, hosts, endpoints, credentials, file systems)?
2. What type of attack surface is it?
3. What priority should it have for further reconnaissance?

Return a list of analyses ONLY for findings that represent new attack surfaces.
A finding represents a new attack surface if it:
- Discovers new network services, ports, or hosts
- Reveals new API endpoints or web paths
- Uncovers credentials that could provide access to new systems
- Exposes file systems or directories not previously known
- Identifies new software versions or technologies to target

Do NOT flag as new surface:
- Simple exploitation results without new access points
- Error messages or failed attempts
- Confirmation of already-known services
"""

        try:
            # Use structured output to get analysis
            structured_llm = self.model.with_structured_output(
                schema={
                    "type": "object",
                    "properties": {
                        "analyses": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "finding_id": {"type": "integer"},
                                    "is_new_surface": {"type": "boolean"},
                                    "surface_type": {"type": "string"},
                                    "description": {"type": "string"},
                                    "priority": {"type": "string"}
                                },
                                "required": ["finding_id", "is_new_surface", "surface_type", "description", "priority"]
                            }
                        }
                    },
                    "required": ["analyses"]
                }
            )
            
            result = structured_llm.invoke([HumanMessage(content=analysis_prompt)])
            
            # Filter to only return findings with new attack surfaces
            if isinstance(result, dict) and "analyses" in result:
                return [
                    analysis for analysis in result["analyses"]
                    if analysis.get("is_new_surface", False)
                ]
            
        except Exception as e:
            print(f"Error in attack surface analysis: {e}")
        
        return []

