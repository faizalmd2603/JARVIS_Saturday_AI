import os
import sys
import json
import asyncio
import logging
from typing import AsyncGenerator, Dict, Any
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api_router import router, AVAILABLE_MODELS
from agents.canva_designer import CanvaDesignerAgent
from agents.notebook_ai import NotebookAIAgent
from agents.career_suite import CareerSuiteAgent
from agents.interviewer_ai import InterviewerAIAgent
from agents.github_studio import GitHubStudioAgent

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [MENTRO-MAIN] %(message)s")

class MentroOrchestrator:
    """
    Mentro AI Superagent Platform Main Orchestrator.
    Routes user prompts to specialized Mentro sub-agents.
    """
    def __init__(self):
        self.name = "MENTRO_PRIME"
        self.agents = {
            "CANVA_DESIGNER": CanvaDesignerAgent(),
            "NOTEBOOK_AI": NotebookAIAgent(),
            "CAREER_SUITE": CareerSuiteAgent(),
            "INTERVIEWER_AI": InterviewerAIAgent(),
            "GITHUB_STUDIO": GitHubStudioAgent()
        }

    def execute_command_sync(self, command: str, model: str = "gemini-3.5-flash-lite", module: str = None, payload: dict = None) -> dict:
        """Synchronous execution handler"""
        cmd_lower = command.lower()

        # Module-specific direct execution
        if module == "canva" or "design" in cmd_lower or "poster" in cmd_lower or "canva" in cmd_lower:
            return self.agents["CANVA_DESIGNER"].execute(command, model=model)
        elif module == "notebook" or "summarize" in cmd_lower or "notes" in cmd_lower or "notebook" in cmd_lower:
            return self.agents["NOTEBOOK_AI"].execute(command, model=model)
        elif module == "career" or "resume" in cmd_lower or "naukri" in cmd_lower or "linkedin" in cmd_lower or "ats" in cmd_lower:
            p = payload or {"user_info": command}
            return self.agents["CAREER_SUITE"].execute(p, model=model)
        elif module == "interview" or "interview" in cmd_lower or "question" in cmd_lower:
            p = payload or {"question": "Tell me about yourself", "answer": command}
            return self.agents["INTERVIEWER_AI"].execute(p, model=model)
        elif module == "github" or "github" in cmd_lower or "code" in cmd_lower or "repo" in cmd_lower:
            p = payload or {"code": command}
            return self.agents["GITHUB_STUDIO"].execute(p, model=model)

        # General completion
        res = router.generate_completion(command, preferred_model=model)
        return {
            "status": "success",
            "agent": self.name,
            "result": res,
            "message": f"Processed via {model}"
        }

    async def route_and_execute_stream(self, command: str, model: str = "gemini-3.5-flash-lite") -> AsyncGenerator[Dict[str, Any], None]:
        """Streaming execution generator for Mentro Web HUD"""
        yield {
            "event": "thinking",
            "agent": self.name,
            "step": f"Analyzing payload with selected model '{model}'...",
            "thought": f"Routing user input: '{command[:60]}...'"
        }

        cmd_lower = command.lower()
        target_agent = "CANVA_DESIGNER"
        reasoning = "Routing to Canva Designer Studio."

        if "resume" in cmd_lower or "career" in cmd_lower or "naukri" in cmd_lower or "linkedin" in cmd_lower:
            target_agent = "CAREER_SUITE"
            reasoning = "Routing to Career Suite & Resume Builder."
        elif "interview" in cmd_lower or "question" in cmd_lower or "eval" in cmd_lower:
            target_agent = "INTERVIEWER_AI"
            reasoning = "Routing to AI Mock Interviewer."
        elif "document" in cmd_lower or "summarize" in cmd_lower or "notes" in cmd_lower or "notebook" in cmd_lower:
            target_agent = "NOTEBOOK_AI"
            reasoning = "Routing to NotebookLM Studio."
        elif "github" in cmd_lower or "code" in cmd_lower or "repo" in cmd_lower:
            target_agent = "GITHUB_STUDIO"
            reasoning = "Routing to GitHub Code Studio."

        yield {
            "event": "agent_selected",
            "target": target_agent,
            "reasoning": reasoning
        }

        yield {
            "event": "executing",
            "agent": target_agent,
            "command": command
        }

        result = self.execute_command_sync(command, model=model, module=target_agent.lower().split("_")[0])

        yield {
            "event": "completed",
            "agent": target_agent,
            "final_response": result.get("message", "Task execution complete."),
            "result": result
        }

orchestrator = MentroOrchestrator()
