import os
import sys
import json
import asyncio
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main_orchestrator import orchestrator
from api_router import AVAILABLE_MODELS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

TEST_CASES = [
    {
        "name": "1. Multi-Model Provider Router Check",
        "module": "general",
        "prompt": "List your core capabilities in 2 bullet points.",
        "model": "gemini-3.5-flash-lite"
    },
    {
        "name": "2. Canva Layered Design Studio",
        "module": "canva",
        "prompt": "Superagent AI Platform Poster",
        "model": "gemini-3.5-flash-lite"
    },
    {
        "name": "3. NotebookLM Studio Synthesis",
        "module": "notebook",
        "prompt": "Mentro AI is a multi-agent system combining Canva, NotebookLM, Naukri, LinkedIn, and GitHub.",
        "model": "gemini-3.5-flash-lite"
    },
    {
        "name": "4. Career Suite Resume Builder",
        "module": "career",
        "prompt": "Lead AI Engineer with experience in Python and FastAPI",
        "model": "gemini-3.5-flash-lite"
    },
    {
        "name": "5. AI Mock Interview Evaluator",
        "module": "interview",
        "prompt": "I handle race conditions using async locks and distributed mutex queues.",
        "model": "gemini-3.5-flash-lite"
    },
    {
        "name": "6. GitHub Code Studio Reviewer",
        "module": "github",
        "prompt": "def calculate_total(items):\n    return sum(item.price for item in items)",
        "model": "gemini-3.5-flash-lite"
    }
]

def run_tests():
    print("\n=======================================================")
    print(" [+] RUNNING MENTRO AI SUPERAGENT PLATFORM TEST SUITE")
    print("=======================================================\n")

    print(f" [+] Total Available Models: {len(AVAILABLE_MODELS)}")
    for m in AVAILABLE_MODELS:
        print(f"     - {m['id']} ({m['name']})")

    passed_count = 0

    for idx, tc in enumerate(TEST_CASES, 1):
        print(f"\n-------------------------------------------------------")
        print(f" [+] TEST {idx}: [{tc['name']}]")
        print(f"     Prompt: '{tc['prompt'][:60]}...'")
        print(f"-------------------------------------------------------")

        try:
            res = orchestrator.execute_command_sync(tc['prompt'], model=tc['model'], module=tc['module'])
            if res and res.get("status") == "success":
                passed_count += 1
                print(f"   [RESULT]: {res.get('message')}")
                print(f"   [DATA]: {json.dumps(res, indent=2)[:300]}...")
            else:
                print(f"   [FAILED]: {res}")
        except Exception as e:
            print(f"   [ERROR]: {e}")

    print("\n=======================================================")
    print(f" [+] MENTRO SUITE TEST COMPLETE: {passed_count}/{len(TEST_CASES)} TESTS PASSED")
    print("=======================================================\n")

if __name__ == "__main__":
    run_tests()
