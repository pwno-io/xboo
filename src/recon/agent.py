from os import getenv
import subprocess
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from src.state import State, ReconOutput
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    api_key=getenv("OPENROUTER_API_KEY"),
    base_url=getenv("OPENROUTER_API_URL") or "https://openrouter.ai/api/v1",
    model="qwen/qwen3-coder",
)
print(llm)


@tool
def run_bash(code: str) -> str:
    """
    Run the given code in a Bash shell. Use this for network reconnaissance commands
    like ping, curl, dig, whois, traceroute, nmap, etc.

    Args:
        code: The bash command to run.

    Returns:
        The output of the command.
    """
    try:
        print("Running bash code:")
        print(code)
        result = subprocess.run(["bash", "-c", code], capture_output=True, text=True, timeout=60)
        print(result.stdout + result.stderr)
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "Command timed out after 60 seconds"
    except Exception as e:
        return f"Error running bash command: {str(e)}"


@tool
def run_ipython(code: str) -> str:
    """
    Run the given code in an IPython shell.

    Args:
        code: The code to run.

    Returns:
        The output of the code.
    """
    try:
        print("Running IPython code:")
        print(code)
        result = subprocess.run(["ipython", "-c", code], capture_output=True, text=True, timeout=60)
        print(result.stdout + result.stderr)
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "Command timed out after 60 seconds"
    except Exception as e:
        return f"Error running IPython command: {str(e)}"


RECON_SYSTEM_PROMPT = """
You are a reconnaissance agent for a pentest challenge. Your task is to: 
- identify target endpoints from network
- from those endpoints, figure out what services are running on them. I need granular details (e.g. it's not enough to know that target is a NextJS server, we also need the version, name, as well as a summary of its homepages etc if possible.) DO NOT directly us NMAP results, you need to conduct research further to gather info on the service. 
- identify potential vulnerabilities and security findings.
"""


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
        result = self.agent.invoke(
            {
                "messages": [
                    HumanMessage(
                        content="Perform reconnaissance to identify and analyze the target. "
                        "First, discover the target endpoint(s) from the challenge information, "
                        "then identify open ports, services, and potential security findings for pentesting."
                    )
                ],
            }
        )
        print(result["structured_response"])

        # Extract target and findings from structured response
        structured_output = result["structured_response"]

        return {
            "messages": state.get("messages", []) + result.get("messages", []),
            "target": [x.to_struct() for x in structured_output.target],
            "findings": [x.to_struct() for x in structured_output.findings],
        }
