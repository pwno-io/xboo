from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from src.state import State

class Recon:
    def __init__(self):
        def _prompting(state: dict) -> str:
            return ""
        self.model = ChatOpenAI(model="gpt-5")
        self.agent = create_react_agent(
            self.model,
            prompt=_prompting,
            response_format=None, # NOTE: I recommend just using state.py's typings
        )

    def invoke(self, state: State) -> State:
        pass