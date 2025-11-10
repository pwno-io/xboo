"""LangGraph-aware tools for scout agents."""

import os
import subprocess

from langchain_core.tools import tool

from src.memory.tools import get_plan, list_memories, store_memory, store_plan
from src.memory.utils import save_plan
from src.utils.problem_api import ProblemAPIClient, AnswerResponse, HintResponse

__all__ = [
    "get_plan",
    "list_memories",
    "run_bash",
    "run_ipython",
    "save_plan",
    "store_memory",
    "store_plan",
    "get_hint",
    "submit_answer",
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

    store all output (temp) file, under /tmp/<ip.replace('.', '-')>-<target-port>/

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


@tool
async def submit_answer(challenge_code: str, answer: str) -> str:
    """
    Submit an answer for a challenge.

    Args:
        challenge_code: The code of the challenge.
        answer: The answer/flag to submit.

    Returns:
        A string describing the result of the submission.
    """
    try:
        async with ProblemAPIClient() as client:
            response: AnswerResponse = await client.submit_answer(challenge_code, answer)
            
            if response.correct:
                return f"Correct! Earned {response.earned_points} points. Challenge is {'solved' if response.is_solved else 'not yet fully solved'}."
            else:
                return f"Incorrect answer. Challenge is {'solved' if response.is_solved else 'not solved'}."
    except Exception as e:  # pylint: disable=broad-except
        return f"Error submitting answer: {str(e)}"


@tool
async def get_hint(challenge_code: str) -> str:
    """
    Retrieve a hint for the specified challenge. 
    (NOTE THAT GET HINT WILL BE PENALIZED, DON'T USE IT UNLESS WE HAVE NO CLUE!)

    Args:
        challenge_code: The code of the challenge to request a hint for.

    Returns:
        A string summarizing the hint content and penalty information.
    """
    try:
        async with ProblemAPIClient() as client:
            response: HintResponse = await client.get_hint(challenge_code)
            hint_intro = "First time using this hint." if response.first_use else "Hint was previously viewed."
            return (
                f"{hint_intro} Penalty: {response.penalty_points} points. "
                f"Hint content: {response.hint_content}"
            )
    except Exception as e:  # pylint: disable=broad-except
        return f"Error retrieving hint: {str(e)}"
