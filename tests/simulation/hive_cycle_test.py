"""
Hive Cycle Simulation
---------------------
Tests the full loop of the Intelligent Hive:
1. Queen Initialization (w/ Router)
2. Task Routing (User Instruction -> Plan)
3. Bee Execution (Scaffolded Bees)
4. Treasury Logic (Budget Check)
"""

import sys
from pathlib import Path

# Add project root to path
current_dir = Path(__file__).resolve().parent
root_dir = current_dir.parent.parent
sys.path.insert(0, str(root_dir))

from hive.queen.orchestrator import QueenOrchestrator


def run_simulation():
    print("==============================================")
    print("       HIVE SOVEREIGN SIMULATION v1.0         ")
    print("==============================================")

    # 1. Initialize Queen
    print("\n[Init] Awakening Queen...")
    queen = QueenOrchestrator(hive_path=root_dir / "hive")

    status = queen.heartbeat()
    print(f"[Status] Queen Alive? {status['queen_status']}")
    print(f"[Status] Intelligence? {status['intelligence_layer']}")
    print(f"[Status] Registered Bees: {len(status['registered_bees'])}")

    # 2. Test Intelligent Routing (Scout + Weather)
    instruction = "Find the latest news on agentic payments and check the weather in Tokyo."
    print(f"\n[Command] '{instruction}'")

    plan_result = queen.orchestrate_complex_task(instruction)

    print("\n[Plan Generated]")
    plan = plan_result.get("plan", {})
    summary = plan.get("intent") or plan.get("plan_summary", "N/A")
    print(f"Summary: {summary}")

    results = plan_result.get("execution_results", [])
    for res in results:
        print(f" > Bee: {res['bee']} | Status: {res['status']}")
        if res["bee"] == "weather":
            print(f"   Output: {res['output'].get('description', 'No description')}")

    # 3. Test Treasury Logic
    pay_instruction = "Transfer 20 USDC to 0x123456789 for server costs."
    print(f"\n[Command] '{pay_instruction}'")

    pay_result = queen.orchestrate_complex_task(pay_instruction)
    pay_exec = pay_result.get("execution_results", [])

    for res in pay_exec:
        print(f" > Bee: {res['bee']} | Status: {res['status']}")
        if res["bee"] == "treasury":
            print(f"   Transaction: {res['output'].get('tx_hash', 'FAILED')}")

    # 4. Test Budget Rejection
    fail_instruction = "Transfer 200 USDC to 0xAttacker."
    print(f"\n[Command] '{fail_instruction}' (Should Fail)")

    fail_result = queen.orchestrate_complex_task(fail_instruction)
    fail_exec = fail_result.get("execution_results", [])
    for res in fail_exec:
        if res["bee"] == "treasury":
            print(f"   Outcome: {res['output'].get('reason')}")

    print("\n==============================================")
    print("       SIMULATION COMPLETE                    ")
    print("==============================================")


if __name__ == "__main__":
    run_simulation()
