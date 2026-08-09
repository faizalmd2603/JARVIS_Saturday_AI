import os
import sys
import json
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from api_router import router

class NotebookAIAgent:
    """
    Mentro NotebookLM Studio Agent:
    Analyzes documents, notes, and research content. Generates executive summaries,
    Q&A knowledge synthesis, and study flashcards.
    """
    def __init__(self):
        self.name = "NOTEBOOK_AI"
        self.role = "NotebookLM Document & Research Synthesizer"

    def execute(self, content: str, action: str = "summarize", model: str = "gemini-3.5-flash-lite") -> dict:
        logging.info(f"[NotebookAI] Processing document action: '{action}'")

        if action == "flashcards":
            system_instruction = """You are Mentro NotebookLM AI.
Extract study flashcards from the text in JSON format:
{
  "summary": "Brief overall synthesis",
  "flashcards": [
    {"question": "Key concept 1?", "answer": "Detailed answer 1"},
    {"question": "Key concept 2?", "answer": "Detailed answer 2"}
  ]
}
"""
            res = router.generate_completion(content, system_instruction=system_instruction, json_mode=True, preferred_model=model)
            try:
                parsed = json.loads(res)
                return {"status": "success", "agent": self.name, "result": parsed, "message": "Extracted flashcards from document."}
            except Exception:
                pass

        # Default: Executive Summary & Synthesis
        system_instruction = """You are Mentro NotebookLM AI Studio.
Provide a high-impact executive synthesis of the user's document/notes including:
1. Executive Overview
2. Key Takeaways & Core Concepts
3. Actionable Insights
4. Suggested Follow-up Questions
"""
        synthesis = router.generate_completion(f"Analyze this document content:\n\n{content}", system_instruction=system_instruction, preferred_model=model)
        return {
            "status": "success",
            "agent": self.name,
            "synthesis": synthesis,
            "message": "Generated NotebookLM document synthesis."
        }
