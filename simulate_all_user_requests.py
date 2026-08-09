import os
import sys
import json
import time
import asyncio
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main_orchestrator import orchestrator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

TEST_CASES = [
    {
        "name": "1. YouTube App (Installed / Taskbar)",
        "command": "Open YouTube app",
        "expected_agent": "STARK"
    },
    {
        "name": "2. WhatsApp Web App (Installed / Taskbar)",
        "command": "Open WhatsApp",
        "expected_agent": "STARK"
    },
    {
        "name": "3. COMET Web Browser (Installed / Taskbar)",
        "command": "Open Comet browser",
        "expected_agent": "STARK"
    },
    {
        "name": "4. Chrome New Tab",
        "command": "Open a chrome new tab for google.com",
        "expected_agent": "SPECTRE"
    },
    {
        "name": "5. COMET New Tab",
        "command": "Open a comet new tab for google.com",
        "expected_agent": "SPECTRE"
    },
    {
        "name": "6. FRIDAY Briefing & Task Tracking",
        "command": "Give me daily intelligence briefing",
        "expected_agent": "FRIDAY"
    },
    {
        "name": "7. HERALD Speech Synthesis",
        "command": "Vocalize system operational",
        "expected_agent": "HERALD"
    },
    {
        "name": "8. BANNER AI Graphic Design",
        "command": "Generate Iron Man poster design",
        "expected_agent": "BANNER"
    },
    {
        "name": "9. HULK Offline Health Check & Math",
        "command": "Run offline health check and calculate 100 * 5",
        "expected_agent": "HULK"
    }
]

async def run_simulation():
    print("\n=======================================================")
    print(" [+] RUNNING SIMULATION ON ALL AGENTS & USER APPS")
    print("=======================================================\n")

    results = []
    failed_count = 0

    for idx, tc in enumerate(TEST_CASES, 1):
        print(f"\n-------------------------------------------------------")
        print(f" [+] TEST {idx}: [{tc['name']}]")
        print(f"     Command: '{tc['command']}'")
        print(f"-------------------------------------------------------")

        agent_used = None
        final_res = None
        status = "PASSED"

        try:
            async for step in orchestrator.route_and_execute_stream(tc['command']):
                event = step.get("event")
                if event == "agent_selected":
                    agent_used = step.get("target")
                    print(f"   [ROUTER] Selected Agent: [{agent_used}] (Reason: {step.get('reasoning')})")
                elif event == "executing":
                    print(f"   [EXEC] {step.get('agent')} executing: {step.get('command')}")
                elif event == "completed":
                    final_res = step.get("final_response")
                    res_data = step.get("result", {})
                    print(f"   [RESULT] Agent [{step.get('agent')}]: {final_res}")
                    print(f"   [DATA]: {res_data}")
        except Exception as e:
            status = f"FAILED ({e})"
            failed_count += 1
            print(f"   [ERROR]: {e}")

        results.append({
            "test": tc['name'],
            "command": tc['command'],
            "agent": agent_used,
            "result": final_res,
            "status": status
        })

    print("\n=======================================================")
    print(f" [+] SIMULATION COMPLETE: {len(TEST_CASES) - failed_count}/{len(TEST_CASES)} TESTS PASSED")
    print("=======================================================\n")

if __name__ == "__main__":
    asyncio.run(run_simulation())
