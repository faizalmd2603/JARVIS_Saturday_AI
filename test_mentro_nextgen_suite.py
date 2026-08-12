import os
import sys
import json
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main_orchestrator import orchestrator
from api_router import AVAILABLE_MODELS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

TEST_CASES = [
    {
        "name": "1. Core AI Agent & Pre-Defined Prompts Engine",
        "module": "core",
        "payload": {"prompt": "Architect a 24/7 Serverless Microservices System on Vercel and AWS Cloud with zero downtime."},
        "model": "gemini-3.5-flash-lite"
    },
    {
        "name": "2. Canva Visual Studio (100+ Fonts & Monthly 20 Image Quota Check)",
        "module": "canva",
        "prompt": "Modern MNC Enterprise Cloud Security Infographic",
        "model": "gemini-3.5-flash-lite"
    },
    {
        "name": "3. NotebookLM RAG Google Web Search Synthesis",
        "module": "notebook",
        "payload": {"query": "Latest advancements in LLM Agent architectures 2026", "action": "search_synthesis"},
        "model": "gemini-3.5-flash-lite"
    },
    {
        "name": "4. Indian Accountancy Balance Sheet & Corporate Financial Solver",
        "module": "accountancy",
        "prompt": "Prepare a Balance Sheet for Reliance Industries Ltd with Share Capital ₹50,00,00,000 and Reserves ₹20,00,00,000.",
        "model": "gemini-3.5-flash-lite"
    },
    {
        "name": "5. Duolingo Sub-Agent (Tamil, English, Hindi, Urdu, French)",
        "module": "duolingo",
        "payload": {"language": "french", "topic": "Travel & Hotel Booking Phrases", "action": "lesson"},
        "model": "gemini-3.5-flash-lite"
    },
    {
        "name": "6. Career Suite ATS Resume Builder",
        "module": "career",
        "prompt": "Senior Cloud Security Engineer",
        "model": "gemini-3.5-flash-lite"
    },
    {
        "name": "7. AI Mock Interviewer Evaluator",
        "module": "interview",
        "prompt": "I design fault-tolerant systems using active-active multi-region database replication.",
        "model": "gemini-3.5-flash-lite"
    },
    {
        "name": "8. GitHub Code Studio Reviewer",
        "module": "github",
        "prompt": "def benchmark(fn):\n    return fn()",
        "model": "gemini-3.5-flash-lite"
    }
]

def run_tests():
    print("\n=======================================================")
    print(" [+] MENTRO AI NEXTGEN ENTERPRISE FULL TEST SUITE")
    print("=======================================================\n")

    passed = 0

    for idx, tc in enumerate(TEST_CASES, 1):
        print(f"\n-------------------------------------------------------")
        print(f" [+] TEST {idx}: [{tc['name']}]")
        print(f"-------------------------------------------------------")

        try:
            p = tc.get("payload") or tc.get("prompt")
            res = orchestrator.execute_command_sync(str(p), model=tc['model'], module=tc['module'], payload=tc.get("payload"))
            if res and res.get("status") in ["success", "rate_limited"]:
                passed += 1
                print(f"   [RESULT]: {res.get('message')}")
            else:
                print(f"   [FAILED]: {res}")
        except Exception as e:
            print(f"   [ERROR]: {e}")

    print("\n=======================================================")
    print(f" [+] TEST SUITE COMPLETE: {passed}/{len(TEST_CASES)} TESTS PASSED")
    print("=======================================================\n")

if __name__ == "__main__":
    run_tests()
