import os
import sys
import json
import logging
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from api_router import router

class GitHubStudioAgent:
    """
    Mentro GitHub Code Studio Agent:
    Inspects GitHub repository URLs, reviews code snippets, generates documentation,
    and identifies performance bottlenecks.
    """
    def __init__(self):
        self.name = "GITHUB_STUDIO"
        self.role = "GitHub Repository & Code Intelligence Agent"

    def execute(self, payload: dict, action: str = "review_code", model: str = "gemini-3.5-flash-lite") -> dict:
        logging.info(f"[GitHubStudio] Executing code action: '{action}'")

        if action == "inspect_repo":
            repo_url = payload.get("repo_url", "https://github.com/faizalmd2603/JARVIS_Saturday_AI")
            # Parse owner and repo name
            clean_path = repo_url.replace("https://github.com/", "").strip("/")
            parts = clean_path.split("/")
            if len(parts) >= 2:
                owner, repo = parts[0], parts[1]
                api_url = f"https://api.github.com/repos/{owner}/{repo}"
                try:
                    res = requests.get(api_url, timeout=5)
                    if res.status_code == 200:
                        repo_info = res.json()
                        summary_prompt = f"Summarize repo {repo_info.get('full_name')}: {repo_info.get('description')}. Language: {repo_info.get('language')}"
                        summary = router.generate_completion(summary_prompt, preferred_model=model)
                        return {
                            "status": "success",
                            "agent": self.name,
                            "repo_details": {
                                "name": repo_info.get("full_name"),
                                "stars": repo_info.get("stargazers_count"),
                                "language": repo_info.get("language"),
                                "description": repo_info.get("description"),
                                "ai_summary": summary
                            },
                            "message": f"Fetched live repository telemetry for '{owner}/{repo}'."
                        }
                except Exception as e:
                    logging.warning(f"[GitHubStudio] GitHub API fetch warning: {e}")

        # Default Action: Code Review & Optimization
        code_snippet = payload.get("code", str(payload))
        system_instruction = """You are Mentro GitHub Code Reviewer.
Analyze the provided code and return JSON:
{
  "code_quality_score": 92,
  "summary": "Clean asynchronous implementation with proper exception handling.",
  "suggestions": [
    "Add type hints to function return signatures",
    "Use connection pooling for HTTP requests"
  ],
  "refactored_code": "# Optimized Version\\n..."
}
"""
        res = router.generate_completion(f"Code to review:\n\n{code_snippet}", system_instruction=system_instruction, json_mode=True, preferred_model=model)
        try:
            parsed = json.loads(res)
            return {"status": "success", "agent": self.name, "review": parsed, "message": "Completed GitHub code review analysis."}
        except Exception as e:
            return {"status": "error", "agent": self.name, "message": f"Code review error: {e}"}
