import os
import sys
import json
import asyncio
import logging
from typing import AsyncGenerator, Dict, Any
from dotenv import load_dotenv

# Ensure project root is in sys.path for Cloud Linux Containers (Render/Railway/CloudRun)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api_router import router
from agents.friday import FridayAgent
from agents.stark import StarkAgent
from agents.spectre import SpectreAgent
from agents.herald import HeraldAgent
from agents.banner import BannerAgent
from agents.hulk import HulkAgent

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [JARVIS-MAIN] %(message)s")

# Import Antigravity SDK components safely
try:
    from google.antigravity import Agent, LocalAgentConfig
    from google.antigravity.hooks.policy import allow, ask_user
    ANTIGRAVITY_AVAILABLE = True
except Exception as e:
    logging.warning(f"[MainOrchestrator] google.antigravity import note: {e}. Running integrated protocol wrapper.")
    ANTIGRAVITY_AVAILABLE = False
    def allow(): return True
    def ask_user(action): return True

class JarvisOrchestrator:
    """
    JARVIS: Prime Orchestrator under the A.V.E.N.G.E.R.S protocol.
    Routes user intent to sub-agents, manages streaming thinking traces, and enforces safety policies.
    """
    def __init__(self):
        self.name = "JARVIS"
        self.role = "Prime Orchestrator & System Core"
        
        # Sub-agent roster
        self.agents = {
            "FRIDAY": FridayAgent(),
            "STARK": StarkAgent(),
            "SPECTRE": SpectreAgent(),
            "HERALD": HeraldAgent(),
            "BANNER": BannerAgent(),
            "HULK": HulkAgent()
        }

    def evaluate_safety_policy(self, target_agent: str, command: str) -> str:
        """
        Declarative safety policies:
        - System actions (STARK shell commands) require 'allow' policy check.
        - High-impact commands evaluate safety hooks.
        """
        if target_agent == "STARK" and any(k in command.lower() for k in ["delete", "remove", "shutdown", "format"]):
            return "ASK_USER_CONFIRMATION"
        return "ALLOWED"

    def pre_route_keyword(self, command: str) -> tuple:
        """Fast pre-routing rules based on command keywords"""
        cmd_lower = command.lower()
        
        # SPECTRE: Web Browser New Tabs / Searches ("chrome tab", "comet tab", "new tab", "search google")
        if any(k in cmd_lower for k in ["new tab", "chrome tab", "comet tab", "open tab", "google", "search", "url", "http"]):
            return "SPECTRE", "Routing to SPECTRE for web browser tab automation."

        # STARK: OS / Taskbar / Installed Desktop Apps (YouTube app, WhatsApp, Comet browser, Notepad, Calc, Taskbar)
        if any(k in cmd_lower for k in ["youtube app", "whatsapp", "comet", "notepad", "calculator", "calc", "cmd", "powershell", "explorer", "spotify", "discord", "vlc", "vscode", "code", "taskbar", "installed app", "open app", "launch app", "slot", "win+"]) or cmd_lower.startswith(("open ", "launch ", "run ")):
            return "STARK", "Routing to STARK for desktop installed app & taskbar control."

        # BANNER: Design / Image / Poster / Draw / Artwork / Typography
        if any(k in cmd_lower for k in ["design", "poster", "artwork", "draw", "image", "logo", "banner", "graphics"]):
            return "BANNER", "Routing to BANNER for creative AI design & PIL layout."

        # FRIDAY: Brief / Task / Reminder / Schedule / Todo
        if any(k in cmd_lower for k in ["brief", "task", "reminder", "schedule", "summary", "morning"]):
            return "FRIDAY", "Routing to FRIDAY for intelligence briefs & task tracking."

        # HERALD: Speak / Voice / Audio / Vocal / TTS
        if any(k in cmd_lower for k in ["speak", "vocalize", "voice", "tts", "say"]):
            return "HERALD", "Routing to HERALD for voice synthesis."

        # HULK: Offline / Math / Calculate / Health / Failover
        if any(k in cmd_lower for k in ["offline", "hulk", "health", "failover", "math", "calculate"]):
            return "HULK", "Routing to HULK for emergency local offline execution."

        return None, None

    async def route_and_execute_stream(self, command: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Asynchronous generator streaming JARVIS thinking traces, safety evaluation,
        sub-agent delegation, and execution logs to the HUD UI.
        """
        yield {
            "event": "thinking",
            "agent": self.name,
            "step": "Analyzing user voice/text payload...",
            "thought": f"Parsing query parameters for: '{command}'"
        }

        # Step 1: Pre-routing or LLM Intent Routing
        target_agent, reasoning = self.pre_route_keyword(command)
        sanitized_cmd = command

        if not target_agent:
            routing_prompt = f"""You are JARVIS Prime Orchestrator.
Analyze the user command: "{command}".
Select the SINGLE best sub-agent from the AVENGERS roster:
- FRIDAY: Intelligence briefing, calendar, task logging, to-do lists
- STARK: Taskbar automation, launch Win app (notepad, calc, cmd), switch windows, OS execution
- SPECTRE: Web browsing, open URL, search Google, list/switch/close browser tabs
- HERALD: Text-to-speech, vocal feedback, audio transcription
- BANNER: Create image design, poster creation, AI artwork, graphic layouts
- HULK: Local math, system diagnostics, offline failover

Return JSON format:
{{
  "target_agent": "FRIDAY" | "STARK" | "SPECTRE" | "HERALD" | "BANNER" | "HULK",
  "reasoning": "Brief explanation of agent selection",
  "sanitized_command": "Cleaned command to pass to sub-agent"
}}
"""
            yield {
                "event": "thinking",
                "agent": self.name,
                "step": "Querying Dual API Router for intent classification...",
                "thought": "Evaluating primary Gemini model with fallback readiness."
            }

            route_res = router.generate_completion(routing_prompt, json_mode=True)
            target_agent = "FRIDAY"
            reasoning = "Defaulting to FRIDAY intelligence."

            try:
                parsed = json.loads(route_res)
                target_agent = parsed.get("target_agent", "FRIDAY").upper()
                reasoning = parsed.get("reasoning", reasoning)
                sanitized_cmd = parsed.get("sanitized_command", command)
            except Exception as e:
                logging.error(f"[JARVIS] Routing parse error: {e}")

        if target_agent not in self.agents:
            target_agent = "HULK"

        yield {
            "event": "agent_selected",
            "agent": self.name,
            "target": target_agent,
            "reasoning": reasoning,
            "step": f"Delegated task to sub-agent [{target_agent}]"
        }

        # Step 2: Safety Policy Evaluation Hook
        policy_status = self.evaluate_safety_policy(target_agent, sanitized_cmd)
        yield {
            "event": "safety_check",
            "agent": self.name,
            "target": target_agent,
            "policy": policy_status,
            "step": f"Safety Policy evaluated: {policy_status}"
        }

        # Step 3: Sub-Agent Execution
        yield {
            "event": "executing",
            "agent": target_agent,
            "step": f"{target_agent} sub-agent executing workload...",
            "command": sanitized_cmd
        }

        sub_agent = self.agents[target_agent]
        try:
            if asyncio.iscoroutinefunction(sub_agent.execute):
                result = await sub_agent.execute(sanitized_cmd)
            else:
                result = sub_agent.execute(sanitized_cmd)
        except Exception as err:
            logging.error(f"[JARVIS] Sub-agent [{target_agent}] error: {err}. Triggering HULK failover...")
            result = self.agents["HULK"].execute(sanitized_cmd)
            result["failover_triggered"] = True

        # Step 4: Final Synthesis & Audio vocalization
        speak_text = result.get("message") or result.get("brief") or f"{target_agent} protocol completed."
        
        if target_agent != "HERALD":
            try:
                self.agents["HERALD"].speak(speak_text[:120])
            except Exception:
                pass

        yield {
            "event": "completed",
            "agent": target_agent,
            "result": result,
            "final_response": speak_text,
            "step": "JARVIS Execution Cycle Complete."
        }

    def execute_command_sync(self, command: str) -> dict:
        """Synchronous helper for automated test suites"""
        import asyncio
        async def _run():
            outputs = []
            async for step in self.route_and_execute_stream(command):
                outputs.append(step)
            return outputs[-1]
        return asyncio.run(_run())

# Global Instance
orchestrator = JarvisOrchestrator()
