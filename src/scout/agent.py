from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from .tool import execution, python
from src.state import State

class Scout:
    def __init__(self):
        def _prompting(state: dict) -> str:
            return "" # system prompt
        self.model = ChatOpenAI(model="gpt-5")
        self.agent = create_react_agent(
            self.model,
            prompt=_prompting,
            response_format=None, # NOTE: I recommend just using state.py's typings
            tools=[execution, python]
        )

    def invoke(self, state: State) -> State:
        result: None = self.agent.invoke( 
            {
                "messages": [
                    HumanMessage(content=
                        f"Do your context engineer here with {state['key']}"
                    ),
                ]
            }
        )
        return {
            "findings": result.get("findings", []),
            "messages": result.get("messages", []),
        }