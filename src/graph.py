from langgraph.graph import StateGraph, END
from src.state import State, GraphNode
from src.recon.agent import Recon
from src.scout.agent import Scout

# Initialize agents
recon = Recon()
scout = Scout()

# Create graph
workflow = StateGraph(State)

# Add nodes
workflow.add_node(GraphNode.RECON, recon.invoke)
workflow.add_node(GraphNode.SCOUT, scout.invoke)

# Set entry point
workflow.set_entry_point(GraphNode.RECON)

# Add conditional edges - Scout determines next step based on route method
workflow.add_conditional_edges(
    GraphNode.SCOUT,
    scout.route,  # Use Scout's route method to determine next step
    {
        GraphNode.RECON: GraphNode.RECON,  # New attack surface found, return to recon
        GraphNode.SCOUT: GraphNode.SCOUT,  # Scout failed and found no new attack surface, return to scout
        GraphNode.END: END,  # Flag found or task complete, end mission
    }
)

# Recon always goes to Scout after completion
workflow.add_edge(GraphNode.RECON, GraphNode.SCOUT)

# Compile graph
graph = workflow.compile()

