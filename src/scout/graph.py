from typing import Optional

from langgraph.graph import END, StateGraph
from langgraph.store.base import BaseStore
from langgraph.store.memory import InMemoryStore

from src.scout.agents import Executor, Pathfinder, Planner
from src.scout.state import ScoutState


def build_graph(store: Optional[BaseStore] = None):
    if store is None:
        store = InMemoryStore()

    pathfinder = Pathfinder()
    planner = Planner()
    executor = Executor()

    graph = (
        StateGraph(ScoutState)
        .add_node("pathfinder", pathfinder.invoke)
        .add_node("planner", planner.invoke)
        .add_node("executor", executor.invoke)
        .set_entry_point("pathfinder")
        .add_edge("pathfinder", "planner")
        .add_edge("planner", "executor")
        .add_edge("executor", END)
    )

    return graph.compile(store=store)