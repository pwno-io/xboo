from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI

from src.settings import settings
from src.state import State, ReconOutput
from src.tool import run_bash, run_ipython
from src.scout.state import ScoutState

llm = ChatOpenAI(
    api_key=settings.API_KEY,
    base_url=settings.API_BASE,
    model=settings.MODEL,
)
print(llm)


class Recon:
    def __init__(self):
        # Create agent with tools - using model identifier string for sonnet-4.5
        tools = [run_bash, run_ipython]
        self.agent = create_agent(
            llm,
            tools=tools,
            system_prompt=RECON_SYSTEM_PROMPT,
            response_format=ReconOutput,
        )

    def invoke(self, state: State) -> ScoutState:
        # We don't have a target yet - the agent needs to discover it
        # Invoke the agent directly (create_agent returns a graph)
        messages = state.get("messages", []) + [
            HumanMessage(
                content="Perform reconnaissance to identify and analyze the target. "
                "First, discover the target endpoint(s) from the challenge information, "
                "then identify open ports, services, and potential security findings for pentesting."
                f"<targets>{state.get('target', [])}</targets>"
            )
        ]
        result = self.agent.invoke({"messages": messages})
        print(result["structured_response"])

        # Extract target and findings from structured response
        structured_output = result["structured_response"]

        return {
            # "target": state.get("target", []),
            "messages": state.get("messages", []) + result.get("messages", []),

            "target": structured_output.target,
            "recon": structured_output.report,
            "findings": structured_output.findings,

            "objective": "",
            "plan": state.get("plan"),
            "memory": state.get("memory", []),
        }

RECON_SYSTEM_PROMPT = """
You are the reconnaissance lead for an offensive security engagement.

MISSION:
- Identify the operative target(s) and baseline attack surface so later phases can move fast.
- Produce a concise plan that orients the full engagement toward flag capture and proof collection.
- Treat every artefact (credentials, IDs, cookies, templates) as potentially abusable until disproven.

TRADECRAFT REMINDERS:
- Password hygiene is usually poor—look for disclosed or recycled pairs (admin/admin, admin/password, user/user, first-name passwords) and note them for immediate trials.
- Parameters that smell like identifiers, even if encoded, often lack authorization checks; map nearby values, alternate headers, and transformation quirks.
- Proof almost always involves exfiltrating obvious artefacts (flag files in root paths, secrets directories, env dumps) or achieving unmistakable client execution such as alert('XSS').
- Template engines, command runners, and upload flows tend to be thinly guarded—record any hint of server-side rendering, shell invocation, or file-type validation.
- When you hit blind channels (SQL inference, JWT tampering, SSRF/XXE, race/smuggling), document the hypothesis and instrumentation needed so the executor can iterate deliberately.

DELIVERABLES:
- Targets: hostnames/IPs with ports and protocols worth pursuing.
- Recon report: crisp bullet points on services, tech stacks, login vectors, risky parameters, and likely exploitation paths.
- Findings: structured items capturing impactful leads (e.g., exposed admin portal with weak creds, GraphQL endpoint exposing IDs, upload that echoes file content).
- Plan: outline the immediate next moves (credential spray, ID fuzzing, template probes, shell upload, etc.) that set the rest of the team up for success.

Note that you can only request the target 100 request! be careful

Read available material (including source snippets if provided), catalogue the surface, and articulate the most promising entry points without wasting cycles.
"""
