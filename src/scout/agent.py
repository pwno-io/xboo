"""Scout agent - Autonomous penetration testing with three-stage workflow."""

from typing import TYPE_CHECKING
from langchain_core.messages import HumanMessage
from src.state import State, Finding, FindingWithFeedback, GraphNodeType
import networkx as nx

from .config import ScoutConfig
from .agents import Strategist, Tactician, Executor
from .analysis import FlagDetector
from .routing import Router
from .utils import MessageBuilder

if TYPE_CHECKING:
    from langchain_openai import ChatOpenAI


class Scout:
    """Scout agent for autonomous penetration testing.
    
    Uses a three-stage workflow:
    1. Strategist: Formulate high-level strategic objectives
    2. Tactician: Break down strategy into executable task DAG
    3. Executor: Execute tasks using available tools
    """
    
    def __init__(self, config: ScoutConfig = None):
        """Initialize Scout with configuration.
        
        Args:
            config: Optional ScoutConfig instance. If None, loads from environment.
        """
        # Load configuration
        self.config = config if config else ScoutConfig.from_env()
        
        # Initialize LLM model
        from langchain_openai import ChatOpenAI
        self.model: ChatOpenAI = ChatOpenAI(
            model=self.config.model_name,
            base_url=self.config.base_url,
            api_key=self.config.api_key,
            temperature=self.config.temperature,
        )
        
        # Initialize specialized agents
        self.strategist = Strategist(self.model)
        self.tactician = Tactician(self.model)
        self.executor = Executor(self.model)
        
        # Initialize utilities
        self.message_builder = MessageBuilder()
        self.flag_detector = FlagDetector()
        self.router = Router(self.model)
    
    def invoke(self, state: State) -> State:
        """Execute three-stage penetration testing workflow.
        
        Args:
            state: Current state with target and findings
            
        Returns:
            Updated state with new findings and messages
        """
        # STAGE 1: STRATEGIST - Define strategic objective
        strategist_message = self.message_builder.build_strategist_message(state)
        strategic_objective = self.strategist.invoke(strategist_message)
        
        # STAGE 2: TACTICIAN - Create task DAG
        tactician_message = self.message_builder.build_tactician_message(
            strategic_objective, state
        )
        task_graph, task_dag = self.tactician.invoke(tactician_message)
        
        # STAGE 3: EXECUTOR - Execute tasks in topological order
        new_findings = self._execute_tasks(
            task_graph, task_dag, strategic_objective, state
        )
        
        # Return updated state
        return {
            "messages": state.get("messages", []) + [
                HumanMessage(content=f"Scout completed: {strategic_objective}")
            ],
            "findings": state.get("findings", []) + new_findings,
            "target": state.get("target"),
        }
    
    def route(self, state: State) -> GraphNodeType:
        """Determine next agent after scout execution.
        
        Args:
            state: Current state with findings
            
        Returns:
            Next graph node (RECON or END)
        """
        return self.router.route(state)
    
    def _execute_tasks(
        self,
        task_graph: dict,
        task_dag: nx.DiGraph,
        strategic_objective: str,
        state: State
    ) -> list[FindingWithFeedback]:
        """Execute tasks from the task graph in topological order.
        
        Args:
            task_graph: Task graph dictionary with nodes and criteria
            task_dag: NetworkX DiGraph for topological sorting
            strategic_objective: Strategic objective from strategist
            state: Current state with target information
            
        Returns:
            List of new findings from task execution
        """
        new_findings = []
        
        # Get task execution order
        try:
            task_order = list(nx.topological_sort(task_dag))
        except:
            task_order = [node["id"] for node in task_graph["nodes"]]
        
        # Execute each task in order
        for task_id in task_order:
            # Find task node details
            task_node = next(
                (n for n in task_graph["nodes"] if n["id"] == task_id),
                None
            )
            if not task_node:
                continue
            
            # Build executor message
            executor_message = self.message_builder.build_executor_message(
                task_node, strategic_objective, state
            )
            
            # Execute task
            output = self.executor.invoke(executor_message)
            
            # Create finding if significant results
            if output and len(output) > 10:
                finding: Finding = {
                    "type": f"scout_{task_node['phase']}",
                    "description": f"{task_node['description']}: {output[:200]}",
                    "severity": "high" if self.flag_detector.detect(output) else "medium",
                    "confidence": "high",
                    "metadata": {
                        "task_id": task_id,
                        "strategic_objective": strategic_objective,
                        "full_output": output,
                        "task_graph": task_graph
                    },
                    "feedback": ""
                }
                new_findings.append(finding)
        
        return new_findings
