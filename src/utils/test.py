from src.scout.agent import Scout
from src.state import State
from langchain_core.messages import HumanMessage

state: State = {
    "messages": [HumanMessage(content="start")],
    "findings": [],
}

scout = Scout()
result = scout.invoke(state)
print("next:", scout.route(result))
print("findings:", len(result["findings"])) 