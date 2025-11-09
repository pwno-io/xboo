from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar, Token
from typing import Any, Iterator, Optional

from langgraph.store.base import BaseStore


_current_store: ContextVar[Optional[BaseStore]] = ContextVar("current_langgraph_store", default=None)
_current_state: ContextVar[Optional[dict[str, Any]]] = ContextVar("current_langgraph_state", default=None)


def get_current_store(optional: bool = False) -> Optional[BaseStore]:
    store = _current_store.get()
    if store is None and not optional:
        raise RuntimeError("LangGraph store is not available in the current context")
    return store


def get_current_state(optional: bool = False) -> Optional[dict[str, Any]]:
    state = _current_state.get()
    if state is None and not optional:
        raise RuntimeError("Agent state is not available in the current context")
    return state


@contextmanager
def memory_context(store: Optional[BaseStore], state: dict[str, Any]) -> Iterator[None]:
    store_token: Optional[Token] = None
    state_token: Optional[Token] = None
    try:
        if store is not None:
            store_token = _current_store.set(store)
        if state is not None:
            state_token = _current_state.set(state)
        yield
    finally:
        if state_token is not None:
            _current_state.reset(state_token)
        if store_token is not None:
            _current_store.reset(store_token)
