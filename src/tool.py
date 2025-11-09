"""Enhanced safe tools for Scout agent with timeouts and error handling."""

from langchain_core.tools import tool
import subprocess
import os


def get_execution_timeout() -> int:
    """Get execution timeout from environment or use default."""
    return int(os.getenv("SCOUT_EXECUTION_TIMEOUT", "30"))


# @sunyxedu's tool
# @tool
# def execution(command: str) -> str:
#     """Execute a shell command and return its output with safety controls.
    
#     Args:
#         command: The shell command to execute
        
#     Returns:
#         The stdout output from the command, or error message
#     """
#     timeout = get_execution_timeout()
    
#     try:
#         result = subprocess.run(
#             command,
#             shell=True,
#             capture_output=True,
#             text=True,
#             timeout=timeout
#         )
        
#         # Return stdout, or stderr if stdout is empty
#         output = result.stdout if result.stdout else result.stderr
#         return output if output else f"Command executed (exit code: {result.returncode})"
        
#     except subprocess.TimeoutExpired:
#         return f"Error: Command timed out after {timeout} seconds"
#     except Exception as e:
#         return f"Error executing command: {str(e)}"


# @tool
# def python(code: str) -> str:
#     """Execute Python code and return its output with safety controls.
    
#     Args:
#         code: The Python code to execute
        
#     Returns:
#         The stdout output from the Python code execution, or error message
#     """
#     timeout = get_execution_timeout()
    
#     try:
#         result = subprocess.run(
#             ["python", "-c", code],
#             capture_output=True,
#             text=True,
#             timeout=timeout
#         )
        
#         # Return stdout, or stderr if stdout is empty
#         output = result.stdout if result.stdout else result.stderr
#         return output if output else f"Python code executed (exit code: {result.returncode})"
        
#     except subprocess.TimeoutExpired:
#         return f"Error: Python code timed out after {timeout} seconds"
#     except Exception as e:
#         return f"Error executing Python code: {str(e)}"


#@JettChenT's tool
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