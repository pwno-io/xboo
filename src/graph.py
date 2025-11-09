from langgraph.graph import StateGraph, END
from src.state import State
from src.recon.agent import Recon
from src.scout.graph import build_graph as Scout
from src.routing.router import Router

def build_graph():
    recon = Recon()
    scout = Scout()
    router = Router()

    graph = (
        StateGraph(State)
        .add_node("recon", recon.invoke)
        .add_node("scout", scout.invoke)

        .set_entry_point("recon")
        .add_edge("recon", "scout")
        .add_conditional_edges(
            "scout",
            router.route,
            {
                "recon": "recon",
                "scout": "scout",
                "end": END,
            }
        )
    )
    return graph.compile()