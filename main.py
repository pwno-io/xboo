from src.recon.agent import Recon
from src.state import State, Target


def main():
    print("🎯 Starting XBOW Reconnaissance Agent\n")

    # Initialize the recon agent
    recon = Recon()

    target: Target = {"ip": "localhost", "port": 3000}

    # Create initial state
    initial_state: State = {"messages": [], "target": target, "findings": []}

    print(f"Target: {target['ip']}:{target['port']}")
    print("=" * 60)
    print("Starting reconnaissance...\n")

    # Invoke the recon agent
    result = recon.invoke(initial_state)

    print("\n" + "=" * 60)
    print("✅ Reconnaissance Complete!")
    print(f"\nMessages: {len(result.get('messages', []))}")
    print(f"Findings: {len(result.get('findings', []))}")

    if result.get("messages"):
        print("\n📋 Agent Output:")
        for msg in result["messages"]:
            if isinstance(msg, str):
                print(msg)
            else:
                print(msg.content if hasattr(msg, "content") else str(msg))


if __name__ == "__main__":
    main()
