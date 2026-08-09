import os
import sys
import json
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from api_router import router

class InterviewerAIAgent:
    """
    Mentro AI Mock Interviewer Agent:
    Simulates technical & behavioral interview rounds for roles (Software Engineer, PM, Data Scientist).
    Provides real-time scoring, constructive feedback, and follow-up questions.
    """
    def __init__(self):
        self.name = "INTERVIEWER_AI"
        self.role = "Interactive Role-Based AI Mock Interviewer"

    def execute(self, payload: dict, action: str = "evaluate", model: str = "gemini-3.5-flash-lite") -> dict:
        logging.info(f"[InterviewerAI] Executing interview action: '{action}'")

        role = payload.get("role", "Software Engineer")

        if action == "generate_question":
            prompt = f"Role: {role}. Difficulty: Mid/Senior Level."
            system_instruction = """You are Mentro Senior Tech Interviewer.
Generate a realistic technical or behavioral interview question in JSON:
{
  "question_id": "q_101",
  "question": "Can you explain how you handle race conditions in distributed multi-agent systems?",
  "category": "System Design & Architecture",
  "hints": ["Mention mutexes, optimistic locking, or event queueing"]
}
"""
            res = router.generate_completion(prompt, system_instruction=system_instruction, json_mode=True, preferred_model=model)
            try:
                parsed = json.loads(res)
                return {"status": "success", "agent": self.name, "interview_question": parsed, "message": f"Generated interview question for {role}."}
            except Exception:
                pass

        # Action: Evaluate Candidate Answer
        question = payload.get("question", "")
        answer = payload.get("answer", "")
        
        prompt = f"Target Role: {role}\nInterview Question: {question}\nCandidate Answer: {answer}"
        system_instruction = """You are Mentro Lead Interviewer Evaluator.
Evaluate the candidate's answer.
Return JSON:
{
  "score": 85,
  "verdict": "STRONG PASS",
  "feedback": "Clear explanation of concurrency concepts. Good mention of async locks.",
  "key_strengths": ["Structured response", "Technical accuracy"],
  "areas_for_improvement": ["Could mention specific message queues like Redis or Kafka"],
  "follow_up_question": "How would you handle network partitions between nodes?"
}
"""
        res = router.generate_completion(prompt, system_instruction=system_instruction, json_mode=True, preferred_model=model)
        try:
            parsed = json.loads(res)
            return {"status": "success", "agent": self.name, "evaluation": parsed, "message": "Evaluated candidate interview response."}
        except Exception as e:
            return {"status": "error", "agent": self.name, "message": f"Evaluation error: {e}"}
