from langchain_core.tools import tool
import subprocess


@tool
def execution(command) -> str:
    return subprocess.run(command, shell=True, capture_output=True, text=True).stdout
@tool
def python(code: str) -> str:
    return subprocess.run(["python", "-c", code], capture_output=True, text=True).stdout