"""LangGraph-native memory tools for scout agents."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, Iterable, Literal, Mapping, Optional
from uuid import uuid4

from langchain.tools import tool, ToolRuntime
from langchain_core.messages import ToolMessage
from langgraph.types import Command

from src.memory.utils import memory_namespace, serialize_store_items

ALLOWED_MEMORY_CATEGORIES = {"plan", "finding", "reflection", "note"}

__all__ = ["store_plan", "get_plan", "list_memories", "store_memory"]


def _state_value(state: Any, key: str, default: Any) -> Any:
    if state is None:
        return default
    if isinstance(state, Mapping):
        return state.get(key, default)
    if hasattr(state, key):
        return getattr(state, key, default)
    return default


def _normalise_plan(plan: Any) -> Dict[str, Any]:
    if plan is None:
        return {}
    if isinstance(plan, dict):
        return plan
    if isinstance(plan, str):
        try:
            parsed = json.loads(plan)
        except json.JSONDecodeError as exc:
            raise ValueError("Plan string must contain valid JSON") from exc
        if isinstance(parsed, dict):
            return parsed
        raise ValueError("Plan JSON must decode to a dictionary object")
    if hasattr(plan, "model_dump"):
        return plan.model_dump()
    if hasattr(plan, "dict"):
        return plan.dict()
    raise ValueError("Plan must be a dictionary-like structure.")


def _coerce_metadata(metadata: Any) -> Dict[str, Any]:
    if metadata is None:
        return {}
    if isinstance(metadata, dict):
        return metadata
    if isinstance(metadata, str):
        try:
            parsed = json.loads(metadata)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError as exc:
            raise ValueError("metadata must be JSON serializable to an object") from exc
    raise ValueError("metadata must be a dict or JSON string representing a dict")


def _dedupe_memories(
    initial: Iterable[Dict[str, Any]], fresh: Iterable[Dict[str, Any]]
) -> list[Dict[str, Any]]:
    combined: list[Dict[str, Any]] = []
    seen: set[str] = set()
    for entry in list(initial) + list(fresh):
        key = entry.get("key") if isinstance(entry, dict) else None
        identifier = key or json.dumps(entry, sort_keys=True, default=str)
        if identifier in seen:
            continue
        seen.add(identifier)
        combined.append(entry)
    return combined


@tool
def store_plan(
    plan: Dict[str, Any],
    runtime: ToolRuntime,
) -> Command:
    """
    Persist the active plan for the current thread.
    """
    state = runtime.state
    store = runtime.store

    normalised_plan = _normalise_plan(plan)
    payload = {"plan": normalised_plan, "updated_at": datetime.utcnow().isoformat()}

    if store is not None:
        namespace = memory_namespace(state, "plan")
        store.put(namespace, "active", payload)

    return Command(
        update={
            "plan": normalised_plan,
            "messages": [
                ToolMessage(
                    content=json.dumps({"status": "plan_stored", "plan": normalised_plan}),
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )


@tool
def get_plan(
    runtime: ToolRuntime,
) -> str:
    """
    Retrieve the current plan snapshot from state or store.
    """
    state = runtime.state
    plan = _state_value(state, "plan", None)
    if plan:
        return json.dumps({"status": "ok", "plan": _normalise_plan(plan)})

    store = runtime.store
    if store is not None:
        namespace = memory_namespace(state, "plan")
        item = store.get(namespace, "active")
        if item:
            value = getattr(item, "value", item)
            if isinstance(value, dict) and "plan" in value:
                return json.dumps({"status": "ok", "plan": value["plan"]})
            if value:
                return json.dumps({"status": "ok", "plan": value})

    return json.dumps({"status": "no_plan_found"})


@tool
def list_memories(
    runtime: ToolRuntime,
) -> str:
    """
    List the stored memory entries scoped to the current thread.
    """
    state = runtime.state
    state_memories = _state_value(state, "memory", []) or []
    if not isinstance(state_memories, list):
        state_memories = list(state_memories)

    store_entries: list[Dict[str, Any]] = []
    store = runtime.store
    if store is not None:
        namespace = memory_namespace(state, "memory")
        items = store.search(namespace)
        for payload in serialize_store_items(items):
            if not isinstance(payload, dict):
                continue
            value = payload.get("value", {})
            if isinstance(value, dict):
                key = payload.get("key")
                if key and "key" not in value:
                    value = {**value, "key": key}
                store_entries.append(value)

    merged = _dedupe_memories(state_memories, store_entries)
    return json.dumps({"status": "ok", "entries": merged})


@tool
def store_memory(
    runtime: ToolRuntime,
    content: Any,
    category: Literal["plan", "finding", "reflection", "note"] = "note",
    metadata: Optional[Any] = None,
) -> Command:
    """
    Persist a structured memory entry for later recall.
    """
    if category not in ALLOWED_MEMORY_CATEGORIES:
        raise ValueError(f"Unsupported memory category '{category}'")

    coerced_metadata = _coerce_metadata(metadata)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "category": category,
        "content": content,
        "metadata": coerced_metadata,
        "key": f"entry-{datetime.utcnow().isoformat()}-{uuid4().hex[:8]}",
    }

    state = runtime.state
    store = runtime.store
    if store is not None:
        namespace = memory_namespace(state, "memory")
        store.put(namespace, entry["key"], entry)

    state_memories = _state_value(state, "memory", []) or []
    if not isinstance(state_memories, list):
        state_memories = list(state_memories)
    updated_memories = state_memories + [entry]

    return Command(
        update={
            "memory": updated_memories,
            "messages": [
                ToolMessage(
                    content=json.dumps({"status": "stored", "entry": entry}),
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )
