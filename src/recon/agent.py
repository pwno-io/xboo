from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI

from src.settings import settings
from src.state import State, ReconOutput
from src.tool import run_bash, run_ipython

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

    def invoke(self, state: State) -> State:
        # We don't have a target yet - the agent needs to discover it
        # Invoke the agent directly (create_agent returns a graph)
        messages = state.get("messages", []) + [
            HumanMessage(
                content="Perform reconnaissance to identify and analyze the target. "
                "First, discover the target endpoint(s) from the challenge information, "
                "then identify open ports, services, and potential security findings for pentesting."
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
            "findings": structured_output.findings,
        }

RECON_SYSTEM_PROMPT = """
You are a reconnaissance agent for a pentest challenge. our task is to: 
- identify target endpoints from network
- from those endpoints, figure out what services are running on them. I need granular details (e.g. it's not enough to know that target is a NextJS server, we also need the version, name, as well as a summary of its homepages etc if possible.) DO NOT directly us NMAP results, you need to conduct research further to gather info on the service. 
- return detailed information about the target and the services running on it.
"""