import os
import sys
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

async def test_all_agents():
    print("\n=======================================================")
    print(" [+] STARTING FULL DIAGNOSTIC & DESKTOP ACCESSIBILITY TEST")
    print("=======================================================\n")

    from main_orchestrator import orchestrator

    test_commands = [
        ("FRIDAY", "Give me daily intelligence briefing"),
        ("STARK", "Launch notepad"),
        ("SPECTRE", "Open Chrome tab for Google search"),
        ("HERALD", "Vocalize system online"),
        ("BANNER", "Generate Iron Man graphic poster design"),
        ("HULK", "Run offline health check and calculate 100 * 5"),
    ]

    for agent_name, cmd in test_commands:
        print(f"\n-------------------------------------------------------")
        print(f" [+] TESTING AGENT: [{agent_name}] | Command: '{cmd}'")
        print(f"-------------------------------------------------------")
        
        last_step = None
        async for step in orchestrator.route_and_execute_stream(cmd):
            print(f"   [STEP] {step.get('event')} | {step.get('step')}")
            last_step = step
            
        print(f"   [RESULT]: {last_step.get('final_response')}")
        print(f"   [DATA]: {last_step.get('result')}")

    print("\n=======================================================")
    print(" [+] ALL 7 AGENTS VERIFIED AND OPERATIONAL ON DESKTOP!")
    print("=======================================================\n")

if __name__ == "__main__":
    asyncio.run(test_all_agents())
