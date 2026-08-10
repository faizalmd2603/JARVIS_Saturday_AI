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
        "name": "1. Multi-Model Router & Rich Markdown Completion",
        "module": "general",
        "prompt": "Provide a 2-bullet markdown summary of enterprise cloud AI platforms.",
        "model": "gemini-3.5-flash-lite"
    },
    {
        "name": "2. Canva & Figma Visual Graphic SVG Studio",
        "module": "canva",
        "prompt": "Enterprise Cloud Architecture Infographic",
        "model": "gemini-3.5-flash-lite"
    },
    {
        "name": "3. NotebookLM Research Synthesis & Flashcards",
        "module": "notebook",
        "payload": {"content": "Machine Learning and Neural Networks principles", "action": "flashcards"},
        "model": "gemini-3.5-flash-lite"
    },
    {
        "name": "4. Indian Accountancy Master Solver (Class 11/12 & Corporate)",
        "module": "accountancy",
        "prompt": "Draft a Balance Sheet for Tata Consultancy Ltd with Share Capital ₹50,00,000 and Reserve Fund ₹12,00,000.",
        "model": "gemini-3.5-flash-lite"
    },
    {
        "name": "5. Duolingo Multilingual Learning (Tamil, English, Hindi, Urdu, French)",
        "module": "duolingo",
        "payload": {"language": "tamil", "topic": "Greetings & Business Expressions", "action": "lesson"},
        "model": "gemini-3.5-flash-lite"
    },
    {
        "name": "6. Career Suite ATS Resume Builder",
        "module": "career",
        "prompt": "Lead Cloud & AI Solutions Architect",
        "model": "gemini-3.5-flash-lite"
    },
    {
        "name": "7. AI Mock Interview Evaluator",
        "module": "interview",
        "prompt": "I design microservices using async REST APIs, Kafka, and Redis caching.",
        "model": "gemini-3.5-flash-lite"
    },
    {
        "name": "8. GitHub Code Studio Inspector",
        "module": "github",
        "prompt": "def compute_hash(val):\n    return hash(val)",
        "model": "gemini-3.5-flash-lite"
    }
]

def run_tests():
    print("\n=======================================================")
    print(" [+] MENTRO AI ENTERPRISE SUITE FULL TEST SUITE")
    print("=======================================================\n")

    passed = 0

    for idx, tc in enumerate(TEST_CASES, 1):
        print(f"\n-------------------------------------------------------")
        print(f" [+] TEST {idx}: [{tc['name']}]")
        print(f"-------------------------------------------------------")

        try:
            p = tc.get("payload") or tc.get("prompt")
            res = orchestrator.execute_command_sync(str(p), model=tc['model'], module=tc['module'], payload=tc.get("payload"))
            if res and res.get("status") == "success":
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
