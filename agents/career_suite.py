import os
import sys
import json
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from api_router import router

class CareerSuiteAgent:
    """
    Mentro Career Suite Agent (Naukri, Internshala, Unstop, LinkedIn):
    Generates ATS-optimized AI Resumes, analyzes Job Description match scores,
    suggests missing skills, and crafts LinkedIn headlines & summaries.
    """
    def __init__(self):
        self.name = "CAREER_SUITE"
        self.role = "Naukri/Internshala/LinkedIn Career & Resume AI"

    def execute(self, payload: dict, action: str = "build_resume", model: str = "gemini-3.5-flash-lite") -> dict:
        logging.info(f"[CareerSuite] Executing career action: '{action}'")

        if action == "ats_match":
            resume_text = payload.get("resume", "")
            job_desc = payload.get("job_description", "")
            prompt = f"Resume:\n{resume_text}\n\nTarget Job Description:\n{job_desc}"
            system_instruction = """You are Mentro ATS Career Coach.
Analyze the match between resume and job description.
Return JSON:
{
  "match_score": 88,
  "missing_keywords": ["Kubernetes", "GraphQL", "CI/CD"],
  "strengths": ["Strong Python experience", "FastAPI web server design"],
  "improvements": ["Highlight cloud deployment achievements", "Quantify metrics"],
  "linkedin_headline": "Senior AI Architect | Python, FastAPI, Multi-Agent Systems"
}
"""
            res = router.generate_completion(prompt, system_instruction=system_instruction, json_mode=True, preferred_model=model)
            try:
                parsed = json.loads(res)
                return {"status": "success", "agent": self.name, "result": parsed, "message": "Calculated ATS Match Score and Keyword Gap Analysis."}
            except Exception:
                pass

        # Action: Build Resume
        user_info = payload.get("user_info", str(payload))
        system_instruction = """You are Mentro Career Suite Resume Builder.
Generate an ATS-optimized professional resume structure in JSON:
{
  "name": "Full Name",
  "title": "Professional Title",
  "summary": "Impactful professional summary...",
  "skills": ["Python", "FastAPI", "React", "Docker", "Machine Learning"],
  "experience": [
    {
      "role": "Lead AI Engineer",
      "company": "Tech Corp",
      "duration": "2023 - Present",
      "highlights": [
        "Architected multi-agent platform serving 10,000+ active users.",
        "Optimized API latency by 45% using async coroutine handlers."
      ]
    }
  ],
  "education": [
    {
      "degree": "B.Tech in Computer Science",
      "institution": "University of Technology",
      "year": "2023"
    }
  ]
}
"""
        res = router.generate_completion(f"User Background Info:\n{user_info}", system_instruction=system_instruction, json_mode=True, preferred_model=model)
        try:
            parsed = json.loads(res)
            return {"status": "success", "agent": self.name, "resume": parsed, "message": "Generated ATS-friendly professional resume."}
        except Exception as e:
            return {"status": "error", "agent": self.name, "message": f"Resume build error: {e}"}
