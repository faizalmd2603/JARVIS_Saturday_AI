import os
import sys
import json
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from api_router import router

PREDEFINED_PROMPTS = [
    {"id": 1, "title": "⚡ Quantum AI & Neural Nets", "prompt": "Explain Quantum Computing & AI Neural Networks in simple terms with key architectural concepts."},
    {"id": 2, "title": "🚀 Serverless Microservices", "prompt": "Architect a 24/7 Serverless Microservices System on Vercel and AWS Cloud with zero downtime."},
    {"id": 3, "title": "💼 Executive Elevator Pitch", "prompt": "Draft an Executive Elevator Pitch for Mentro AI Enterprise Superagent Platform for VC investors."},
    {"id": 4, "title": "📊 Financial & AI Market Trends", "prompt": "Analyze global financial markets, corporate accounting standards, and AI startup growth trends 2026."}
]

class CoreAIAgent:
    """
    Mentro Core AI Agent:
    Gemini-style text chatbot supporting pre-defined prompts, RAG web search context,
    and camera hand-gesture control.
    """
    def __init__(self):
        self.name = "CORE_AI"
        self.role = "Gemini Core AI Assistant & Camera Gesture Controller"

    def execute(self, payload: dict, model: str = "gemini-3.5-flash-lite") -> dict:
        prompt = payload.get("prompt", "")
        gesture = payload.get("gesture")
        
        logging.info(f"[CORE_AI] Executing query: '{prompt[:40]}...' (Gesture: {gesture})")

        system_instruction = """You are Mentro Core AI Agent (Gemini-style AI Assistant).
Provide a high-impact, beautifully formatted Markdown response with headings, bullet points, bold emphasis, and structured tables where helpful.
If hand gestures are detected, acknowledge the gesture control mode."""

        res_md = router.generate_completion(prompt, system_instruction=system_instruction, preferred_model=model)
        
        return {
            "status": "success",
            "agent": self.name,
            "prompt": prompt,
            "gesture_detected": gesture,
            "response_markdown": res_md,
            "predefined_prompts": PREDEFINED_PROMPTS,
            "message": "Processed Core AI Agent query."
        }
