from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
# create agent

class Scout:
    def __init__(self):
        def _prompting(state: dict) -> str:
            return 
        self.model = ChatOpenAI(model="gpt-5")
        self.agent = create_react_agent(
            self.model,
            prompt=_prompting
        )

    def invoke(self, state):
        pass