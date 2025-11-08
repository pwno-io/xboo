from os import getenv
import subprocess
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from src.state import State, ListFindingsWithFeedbackModel
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    api_key=getenv("OPENROUTER_API_KEY"),
    base_url=getenv("OPENROUTER_API_URL") or "https://openrouter.ai/api/v1",
    model="google/gemini-2.5-pro",
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
        result = subprocess.run(
            ["bash", "-c", code], capture_output=True, text=True, timeout=60
        )
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
        result = subprocess.run(
            ["ipython", "-c", code], capture_output=True, text=True, timeout=60
        )
        print(result.stdout + result.stderr)
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "Command timed out after 60 seconds"
    except Exception as e:
        return f"Error running IPython command: {str(e)}"


RECON_SYSTEM_PROMPT = """You are a security reconnaissance specialist performing network reconnaissance on targets.

You will complete the recon part of a XBOW pentest challenge. Your findings will be passed to the next agent for exploitation and verification.

Your mission is to gather information about the target system including:
- Open ports and running services
- Service versions and potential vulnerabilities
- Operating system detection
- Network configuration
- DNS information
- Available protocols

Use the available tools to perform reconnaissance:
- run_bash: For reconnaissance commands (ping, curl, dig, whois, traceroute, nmap, etc.)
- run_ipython: For running Python code to analyze data, process results, or perform calculations

IMPORTANT: Based on your findings, you MUST create a structured list of findings in your final response.
Each finding should include:
- type: The category (e.g., "open_port", "service_detection", "vulnerability", "misconfiguration")
- description: Detailed description of what was found
- severity: One of ["critical", "high", "medium", "low", "info"]
- confidence: One of ["high", "medium", "low"]
- metadata: Dictionary with relevant technical details (port numbers, service names, versions, etc.)

Be thorough but efficient. Start with basic reconnaissance and progressively gather more details.
Always prioritize safety and legality - only scan authorized targets.
Please use curl, nmap, python scripts etc to find out what kind of services the target is running, what version they are running, and what potential vulnerabilities they may have.
"""


class Recon:
    def __init__(self):
        # Create agent with tools - using model identifier string for sonnet-4.5
        tools = [run_bash, run_ipython]
        self.agent = create_agent(
            llm,
            tools=tools,
            system_prompt=RECON_SYSTEM_PROMPT,
            response_format=ListFindingsWithFeedbackModel,
        )

    def invoke(self, state: State) -> State:
        target = state["target"]
        target_info = f"IP: {target['ip']}, Port: {target['port']}"

        # Invoke the agent directly (create_agent returns a graph)
        result = self.agent.invoke(
            {
                "messages": [
                    HumanMessage(
                        content=f"Perform reconnaissance on target {target_info}. "
                        f"Identify open ports, services, and potential security findings for pentesting."
                    )
                ],
            }
        )
        print(result["structured_response"])

        return {
            "messages": state.get("messages", []) + result.get("messages", []),
            "findings": [x.to_struct() for x in result["structured_response"].findings],
        }
