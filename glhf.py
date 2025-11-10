"""Competition runner that starts at 10am and runs challenges in parallel."""

import asyncio
import datetime
from typing import List
from langgraph.store.memory import InMemoryStore

from src.graph import build_graph
from src.utils.problem_api import ProblemAPIClient, Challenge
from src.state import State, Target
from langchain_core.messages import HumanMessage


async def run_single_challenge(challenge: Challenge, graph_index: int):
    """Run a single challenge in its own graph instance."""
    print(f"[Graph {graph_index}] Starting challenge: {challenge.challenge_code}")
    
    # Create separate store for each graph instance
    store = InMemoryStore()
    
    # Build the graph with its own store
    graph = build_graph()
    
    # Prepare initial state with challenge information
    initial_state = State(
        messages=[],
        target=[
            Target(ip=challenge.target_info.ip, port=port) 
            for port in challenge.target_info.port
        ],
        recon="",
        findings=[],
        flag="",
        redirection=[]
    )
    
    try:
        # Run the graph
        result = await graph.ainvoke(
            initial_state,
            store=store,
            config={"recursion_limit": 100},
        )
        print(f"[Graph {graph_index}] Completed challenge: {challenge.challenge_code}")
        if result.get("flag"):
            print(f"[Graph {graph_index}] Found flag: {result['flag']}")
        return result
    except Exception as e:
        print(f"[Graph {graph_index}] Error in challenge {challenge.challenge_code}: {str(e)}")
        return None


async def wait_15_minutes():
    """Wait for 15 minutes."""
    wait_seconds = 15 * 60  # 15 minutes in seconds
    start_time = datetime.datetime.now()
    target_time = start_time + datetime.timedelta(seconds=wait_seconds)
    
    print(f"Current time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Will start at: {target_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Waiting for 15 minutes...")
    
    # Wait with periodic updates
    while datetime.datetime.now() < target_time:
        elapsed = (datetime.datetime.now() - start_time).total_seconds()
        remaining = wait_seconds - elapsed
        
        if remaining > 60:
            print(f"Still waiting... {remaining / 60:.1f} minutes remaining")
            await asyncio.sleep(60)  # Sleep for 1 minute
        else:
            print(f"Almost time! {remaining:.0f} seconds remaining")
            await asyncio.sleep(1)  # Sleep for 1 second
    
    print("Wait complete! Starting competition...")


async def run_competition(skip_wait: bool = False):
    """Main competition runner."""
    if not skip_wait:
        await wait_15_minutes()
    
    print("\n🏁 COMPETITION STARTING! 🏁\n")
    
    # Get challenges from API
    try:
        async with ProblemAPIClient() as client:
            challenges_response = await client.get_challenges()
            
        print(f"Stage: {challenges_response.current_stage}")
        print(f"Total challenges: {len(challenges_response.challenges)}")
        
        # Filter out already solved challenges
        unsolved_challenges = [c for c in challenges_response.challenges if not c.solved]
        print(f"Unsolved challenges: {len(unsolved_challenges)}")
        
        if not unsolved_challenges:
            print("All challenges are already solved! 🎉")
            return
        
        # Run all unsolved challenges in parallel
        tasks = []
        for i, challenge in enumerate(unsolved_challenges):
            task = asyncio.create_task(run_single_challenge(challenge, i))
            tasks.append(task)
        
        print(f"\nStarting {len(tasks)} parallel graph instances...\n")
        
        # Wait for all challenges to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Retry any challenges that failed due to errors
        failed_indices = [
            idx
            for idx, result in enumerate(results)
            if isinstance(result, Exception) or result is None
        ]

        if failed_indices:
            print("\nRetrying failed challenges...\n")
            retry_tasks = [
                asyncio.create_task(run_single_challenge(unsolved_challenges[idx], idx))
                for idx in failed_indices
            ]
            retry_results = await asyncio.gather(*retry_tasks, return_exceptions=True)
            for idx, retry_result in zip(failed_indices, retry_results):
                results[idx] = retry_result
        
        # Print summary
        print("\n📊 COMPETITION RESULTS 📊")
        successful = sum(1 for r in results if r and not isinstance(r, Exception))
        print(f"Successful completions: {successful}/{len(tasks)}")
        
        for i, (challenge, result) in enumerate(zip(unsolved_challenges, results)):
            if isinstance(result, Exception):
                print(f"Challenge {challenge.challenge_code}: ❌ Error - {result}")
            elif result is None:
                print(
                    f"Challenge {challenge.challenge_code}: ❌ Error - graph did not return a result"
                )
            elif result and result.get("flag"):
                print(f"Challenge {challenge.challenge_code}: ✅ Flag found!")
            else:
                print(f"Challenge {challenge.challenge_code}: ⚠️ Completed but no flag found")
                
    except Exception as e:
        print(f"Error getting challenges: {str(e)}")


async def main():
    """Main entry point."""
    import sys
    
    # Check if --now flag is passed to skip waiting
    skip_wait = "--now" in sys.argv
    
    if skip_wait:
        print("Skipping wait, starting immediately...")
    
    await run_competition(skip_wait=skip_wait)


if __name__ == "__main__":
    asyncio.run(main())
