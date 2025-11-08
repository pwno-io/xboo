from src.recon.agent import Recon
from src.scout.agent import Scout
from src.state import State, Target
from langchain_core.messages import HumanMessage


def main():
    print("🎯 Starting XBOW Reconnaissance Agent\n")

    # Initialize the recon agent
    recon = Recon()
    initial_context = "CHALLENGE: Trading Platform. The target is in localhost:32768."

    # Create initial state
    initial_state: State = {
        "messages": [
            HumanMessage(content=initial_context),
            HumanMessage(content="Please solve the challenge and find the flag."),
        ],
        "target": [],
        "findings": [],
    }

    print("=" * 60)
    print("Starting reconnaissance...\n")

    # Invoke the recon agent
    result = recon.invoke(initial_state)

    print("=" * 60)
    print("Starting scout...\n")
    scout = Scout()
    scout_result = scout.invoke(result)
    print("scout_result:", scout_result)
    print(scout.route(scout_result))


if __name__ == "__main__":
    main()
