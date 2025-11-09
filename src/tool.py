"""LangGraph-aware tools for scout agents."""

import json
import os
import subprocess
from datetime import datetime
from typing import Any, Dict, Literal, Optional

from langchain_core.tools import tool

from src.memory.context import get_current_state, get_current_store
from src.memory.utils import append_memory_entry, list_memory_entries, load_plan, save_plan

ALLOWED_MEMORY_CATEGORIES = {"plan", "finding", "reflection", "note"}


def get_execution_timeout() -> int:
    """Get execution timeout from environment or use default."""
    return int(os.getenv("SCOUT_EXECUTION_TIMEOUT", "30"))


def _sanitize_metadata(metadata: Optional[Dict[str, Any]]) -> Dict[str, str]:
    if not metadata:
        return {}
    clean: Dict[str, str] = {}
    for key, value in metadata.items():
        clean[str(key)] = str(value)
    return clean


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
    except Exception as e:  # pylint: disable=broad-except
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
    except Exception as e:  # pylint: disable=broad-except
        return f"Error running IPython command: {str(e)}"


def _ensure_plan_dict(content: Any) -> Dict[str, Any]:
    if isinstance(content, dict):
        return content
    if isinstance(content, str):
        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:  # pragma: no cover - defensive
            raise ValueError("content must be valid JSON when storing a plan") from exc
    raise ValueError("content must be a dict or JSON string when storing a plan")


@tool
def memory_log(
    action: Literal["store_plan", "get_plan", "list", "store"],
    content: Optional[Any] = None,
    category: Literal["plan", "finding", "reflection", "note"] = "note",
    metadata: Optional[Dict[str, Any]] = None,
) -> str:

    store = get_current_store(optional=True)
    state = get_current_state(optional=True)
    if store is None:
        return json.dumps({"status": "store_unavailable"})

    if action == "store_plan":
        if content is None:
            raise ValueError("content is required for store_plan action")
        plan_dict = _ensure_plan_dict(content)
        save_plan(plan_dict, state=state, store=store)
        return json.dumps({"status": "plan_stored", "plan": plan_dict})

    if action == "get_plan":
        plan_payload = load_plan(state=state, store=store)
        return json.dumps({"status": "ok", "plan": plan_payload})

    if action == "list":
        entries = list_memory_entries(state=state, store=store)
        return json.dumps({"status": "ok", "entries": entries})

    if action == "store":
        if not content:
            raise ValueError("content is required for store action")

        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "category": category,
            "content": str(content),
            "metadata": _sanitize_metadata(metadata),
        }
        stored_entry = append_memory_entry(entry, state=state, store=store)
        return json.dumps({"status": "stored", "entry": stored_entry})

    raise ValueError(f"Unsupported memory action '{action}'.")


def store_plan_to_memory(plan: Dict[str, Any], state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Persist the provided plan payload to the LangGraph memory store."""
    return save_plan(plan, state=state)