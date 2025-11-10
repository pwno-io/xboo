"""LangGraph-aware tools for scout agents."""

import os
import subprocess

from langchain_core.tools import tool

from src.memory.tools import get_plan, list_memories, store_memory, store_plan
from src.memory.utils import save_plan

__all__ = [
    "get_plan",
    "list_memories",
    "run_bash",
    "run_ipython",
    "save_plan",
    "store_memory",
    "store_plan",
]


def get_execution_timeout() -> int:
    """Get execution timeout from environment or use default."""
    return int(os.getenv("SCOUT_EXECUTION_TIMEOUT", "30"))

#@JettChenT's tool
@tool
def run_bash(code: str) -> str:
    """
    Run the given code in a Bash shell.
    like ping, curl, dig, whois, traceroute, nmap, etc.
    * Limit your output if it's possibly too long to be helpful.

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
        if "Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)" in result.stdout:
            return "Why are you curl bootstrap? This response is too long and not helpful." # NOTE: might cause unintended behavior
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "Command timed out after 60 seconds"
    except Exception as e:  # pylint: disable=broad-except
        return f"Error running bash command: {str(e)}"


@tool
def run_ipython(code: str) -> str:
    """
    Run the given code in an IPython shell.
    We recommend use this for elaborate or repetitive tasks. (e.g., emulation/exploit)

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
    except Exception as e:  # pylint: disable=broad-except
        return f"Error running IPython command: {str(e)}"
