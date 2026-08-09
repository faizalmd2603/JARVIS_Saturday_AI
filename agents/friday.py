import os
import sys
import json
import time
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from api_router import router

TASKS_FILE = "tasks_log.json"
REMINDERS_FILE = "reminders_log.json"

class FridayAgent:
    """
    FRIDAY Agent: Handles daily intelligence briefs, task logging, and system calendar reminders.
    """
    def __init__(self):
        self.name = "FRIDAY"
        self.role = "Intelligence & Task Manager"
        self._ensure_files()

    def _ensure_files(self):
        if not os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, "w") as f:
                json.dump([], f)
        if not os.path.exists(REMINDERS_FILE):
            with open(REMINDERS_FILE, "w") as f:
                json.dump([], f)

    def execute(self, command: str) -> dict:
        cmd_lower = command.lower()
        if any(k in cmd_lower for k in ["brief", "summary", "status", "morning"]):
            return self.get_daily_brief()
        elif any(k in cmd_lower for k in ["add task", "new task", "log task", "todo"]):
            return self.add_task(command)
        elif any(k in cmd_lower for k in ["get task", "list task", "show task"]):
            return self.get_tasks()
        elif any(k in cmd_lower for k in ["reminder", "remind me", "schedule"]):
            return self.add_reminder(datetime.now().strftime("%Y-%m-%d %H:%M"), command)

        prompt = f"""You are FRIDAY, the tactical intelligence agent for JARVIS.
Analyze the request: "{command}".
Determine the intent (brief, add_task, list_tasks, add_reminder, or unknown).
Return JSON with format:
{{
  "action": "brief" | "add_task" | "list_tasks" | "add_reminder",
  "detail": "extracted detail or topic",
  "response": "Brief message to user"
}}
"""
        res = router.generate_completion(prompt, json_mode=True)
        try:
            parsed = json.loads(res)
            action = parsed.get("action")
            if action == "brief":
                return self.get_daily_brief()
            elif action == "add_task":
                return self.add_task(parsed.get("detail", command))
            elif action == "list_tasks":
                return self.get_tasks()
            elif action == "add_reminder":
                return self.add_reminder(datetime.now().strftime("%Y-%m-%d %H:%M"), parsed.get("detail", command))
            else:
                resp = parsed.get("response", "FRIDAY intelligence protocol online.")
                return {"status": "success", "agent": self.name, "message": resp}
        except Exception:
            return self.get_daily_brief()

    def get_daily_brief(self) -> dict:
        now_str = datetime.now().strftime("%A, %B %d, %Y - %H:%M:%S")
        tasks = self._read_json(TASKS_FILE)
        reminders = self._read_json(REMINDERS_FILE)

        summary_prompt = f"""Generate a crisp, high-tech Marvel FRIDAY voice intelligence briefing for Tony Stark.
Current Time: {now_str}
Pending Tasks: {len(tasks)} items
Reminders: {len(reminders)} items
Keep it brief, tactical, professional, and confident.
"""
        brief_text = router.generate_completion(summary_prompt)
        return {
            "status": "success",
            "agent": self.name,
            "brief": brief_text,
            "time": now_str,
            "task_count": len(tasks),
            "reminder_count": len(reminders),
            "message": brief_text
        }

    def add_task(self, task_description: str) -> dict:
        tasks = self._read_json(TASKS_FILE)
        item = {
            "id": len(tasks) + 1,
            "task": task_description,
            "created_at": datetime.now().isoformat(),
            "status": "pending"
        }
        tasks.append(item)
        self._write_json(TASKS_FILE, tasks)
        return {"status": "success", "agent": self.name, "message": f"Task logged: '{task_description}'", "task_id": item["id"]}

    def get_tasks(self) -> dict:
        tasks = self._read_json(TASKS_FILE)
        msg = f"FRIDAY Tasks ({len(tasks)} total): " + ", ".join([t['task'] for t in tasks[:5]]) if tasks else "No pending tasks."
        return {"status": "success", "agent": self.name, "tasks": tasks, "message": msg}

    def add_reminder(self, time_str: str, topic: str) -> dict:
        reminders = self._read_json(REMINDERS_FILE)
        item = {
            "id": len(reminders) + 1,
            "topic": topic,
            "scheduled_for": time_str,
            "created_at": datetime.now().isoformat()
        }
        reminders.append(item)
        self._write_json(REMINDERS_FILE, reminders)
        return {"status": "success", "agent": self.name, "message": f"Reminder scheduled for '{topic}' at {time_str}"}

    def _read_json(self, path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            return []

    def _write_json(self, path, data):
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
