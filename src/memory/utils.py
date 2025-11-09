from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence, Tuple
from uuid import uuid4

from langgraph.store.base import BaseStore

from src.memory.context import get_current_state, get_current_store

Namespace = Tuple[str, ...]


def _first_target(state: Mapping[str, Any] | None) -> str:
    if not state:
        return "global"
    # Handle both dict-like and Pydantic model states
    if hasattr(state, 'target'):
        targets = state.target if state.target else []
    else:
        targets = state.get("target", []) or []
    if not targets:
        return "global"
    primary = targets[0]
    # Handle both dict and Pydantic model targets
    if hasattr(primary, 'ip'):
        ip = primary.ip if primary.ip else "unknown"
        port = primary.port if hasattr(primary, 'port') else None
    else:
        ip = primary.get("ip", "unknown")
        port = primary.get("port")
    if port is None:
        return f"{ip}"
    return f"{ip}:{port}"


def memory_namespace(state: Mapping[str, Any] | None, scope: str) -> Namespace:
    target_label = _first_target(state)
    return ("scout", target_label, scope)


def serialize_store_items(items: Iterable[Any]) -> Sequence[Dict[str, Any]]:
    serialised: list[Dict[str, Any]] = []
    for item in items:
        key = getattr(item, "key", None)
        value = getattr(item, "value", item)
        if hasattr(value, "model_dump"):
            value = value.model_dump()
        serialised.append({"key": key, "value": value})
    return serialised


def save_plan(plan: Dict[str, Any], *, state: Optional[Mapping[str, Any]] = None, store: Optional[BaseStore] = None) -> Dict[str, Any]:
    store = store or get_current_store(optional=True)
    if store is None:
        return {}
    state = state or get_current_state(optional=True)
    namespace = memory_namespace(state, "plan")
    payload = {"plan": plan, "updated_at": datetime.utcnow().isoformat()}
    store.put(namespace, "active", payload)
    return payload


def load_plan(*, state: Optional[Mapping[str, Any]] = None, store: Optional[BaseStore] = None) -> Optional[Dict[str, Any]]:
    store = store or get_current_store(optional=True)
    if store is None:
        return None
    state = state or get_current_state(optional=True)
    namespace = memory_namespace(state, "plan")
    items = store.get(namespace, "active")
    if not items:
        return None
    item = items[0]
    value = getattr(item, "value", item)
    if isinstance(value, dict) and "plan" in value:
        return value["plan"]
    return value


def append_memory_entry(
    entry: Dict[str, Any],
    *,
    state: Optional[Mapping[str, Any]] = None,
    store: Optional[BaseStore] = None,
) -> Dict[str, Any]:
    store = store or get_current_store(optional=True)
    if store is None:
        return {}
    state = state or get_current_state(optional=True)
    namespace = memory_namespace(state, "memory")
    key = f"entry-{datetime.utcnow().isoformat()}-{uuid4().hex[:8]}"
    store.put(namespace, key, entry)
    return {"key": key, **entry}


def list_memory_entries(
    *,
    state: Optional[Mapping[str, Any]] = None,
    store: Optional[BaseStore] = None,
) -> Sequence[Dict[str, Any]]:
    store = store or get_current_store(optional=True)
    if store is None:
        return []
    state = state or get_current_state(optional=True)
    namespace = memory_namespace(state, "memory")
    items = store.search(namespace)
    return serialize_store_items(items)
