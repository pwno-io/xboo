from langgraph.graph import StateGraph, END

from src.scout.state import ScoutState
from src.scout.agents import Strategist, Tactician, Executor

def build_graph():

    strategist = Strategist()
    tactician = Tactician()
    executor = Executor()

    graph = (
        StateGraph(ScoutState)
        .add_node("strategist", strategist.invoke)
        .add_node("tactician", tactician.invoke)

        .add_node("executor", executor.invoke)
        .set_entry_point("strategist")

        .add_edge("strategist", "tactician")
        .add_edge("tactician", "executor")
        .add_edge("executor", END)
    )

    return graph.compile()