"""Enhanced safe tools for Scout agent with timeouts and error handling."""

from langchain_core.tools import tool
import subprocess
import os


def get_execution_timeout() -> int:
    """Get execution timeout from environment or use default."""
    return int(os.getenv("SCOUT_EXECUTION_TIMEOUT", "30"))


@tool
def execution(command: str) -> str:
    """Execute a shell command and return its output with safety controls.
    
    Args:
        command: The shell command to execute
        
    Returns:
        The stdout output from the command, or error message
    """
    timeout = get_execution_timeout()
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        # Return stdout, or stderr if stdout is empty
        output = result.stdout if result.stdout else result.stderr
        return output if output else f"Command executed (exit code: {result.returncode})"
        
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout} seconds"
    except Exception as e:
        return f"Error executing command: {str(e)}"


@tool
def python(code: str) -> str:
    """Execute Python code and return its output with safety controls.
    
    Args:
        code: The Python code to execute
        
    Returns:
        The stdout output from the Python code execution, or error message
    """
    timeout = get_execution_timeout()
    
    try:
        result = subprocess.run(
            ["python", "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        # Return stdout, or stderr if stdout is empty
        output = result.stdout if result.stdout else result.stderr
        return output if output else f"Python code executed (exit code: {result.returncode})"
        
    except subprocess.TimeoutExpired:
        return f"Error: Python code timed out after {timeout} seconds"
    except Exception as e:
        return f"Error executing Python code: {str(e)}"

