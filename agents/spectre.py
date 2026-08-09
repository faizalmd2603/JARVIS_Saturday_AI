import os
import sys
import json
import asyncio
import logging
import urllib.parse
import subprocess
import webbrowser

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from api_router import router

user_profile = os.environ.get("USERPROFILE", r"C:\Users\Default")

CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.join(user_profile, r"AppData\Local\Google\Chrome\Application\chrome.exe")
]

COMET_PATHS = [
    os.path.join(user_profile, r"AppData\Local\Perplexity\Comet\Application\comet.exe"),
    os.path.join(user_profile, r"AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Comet.lnk"),
    os.path.join(user_profile, r"AppData\Roaming\Microsoft\Internet Explorer\Quick Launch\User Pinned\TaskBar\Comet.lnk"),
    r"C:\Program Files\Comet\Application\comet.exe",
    r"C:\Program Files (x86)\Comet\Application\comet.exe"
]

def launch_desktop_chrome(url: str) -> bool:
    """Launches Chrome browser tab directly on desktop screen."""
    logging.info(f"[SPECTRE] Initiating Chrome browser tab launch for: {url}")
    
    # Direct Chrome executable launch
    for cp in CHROME_PATHS:
        if os.path.exists(cp):
            try:
                logging.info(f"[SPECTRE] Found Chrome executable: {cp}")
                subprocess.Popen([cp, "--new-window", url])
                return True
            except Exception as ex:
                logging.warning(f"[SPECTRE] Chrome path launch error: {ex}")

    # ShellExecute start
    try:
        os.system(f'cmd /c start "" "{url}"')
        return True
    except Exception as e:
        logging.error(f"[SPECTRE] Chrome tab launch failed: {e}")
        return False

def launch_desktop_comet(url: str) -> bool:
    """Launches Comet browser tab directly on desktop screen."""
    logging.info(f"[SPECTRE] Initiating Comet browser tab launch for: {url}")
    
    for path in COMET_PATHS:
        if os.path.exists(path):
            try:
                logging.info(f"[SPECTRE] Found Comet path: {path}")
                if path.endswith(".exe"):
                    subprocess.Popen([path, url])
                else:
                    os.system(f'cmd /c start "" "{path}" "{url}"')
                return True
            except Exception as ex:
                logging.warning(f"[SPECTRE] Comet launch error for {path}: {ex}")

    # Fallback to shell start
    try:
        os.system(f'cmd /c start comet "{url}"')
        return True
    except Exception as e:
        logging.error(f"[SPECTRE] All Comet launch strategies failed: {e}")
        return False

class SpectreAgent:
    """
    SPECTRE / Browser Agent: Web browser tab controller for Chrome and Comet browsers.
    Supports opening new tabs, Google search, and targeted browser execution.
    """
    def __init__(self):
        self.name = "SPECTRE"
        self.role = "Browser & Tab Automation Agent"

    async def execute(self, command: str) -> dict:
        cmd_lower = command.lower()
        
        # Target browser detection
        browser_type = "chrome"
        if "comet" in cmd_lower:
            browser_type = "comet"

        prompt = f"""You are SPECTRE, the web browser tab controller sub-agent for JARVIS.
Analyze user command: "{command}".
Determine intended action and target URL/query:
1. "open": Open specific URL (e.g. google.com, youtube.com)
2. "search": Search Google for query

Return JSON:
{{
  "action": "open" | "search",
  "url": "https://..." (if open),
  "query": "search query" (if search),
  "browser": "{browser_type}"
}}
"""
        res = router.generate_completion(prompt, json_mode=True)
        try:
            parsed = json.loads(res)
            action = parsed.get("action", "search")
            target_browser = parsed.get("browser", browser_type)
            
            if "comet" in cmd_lower:
                target_browser = "comet"

            if action == "open":
                url = parsed.get("url") or "https://google.com"
                if not url.startswith("http"):
                    url = "https://" + url
                return await self.open_tab(url, browser=target_browser)
            else:
                q = parsed.get("query") or command
                return await self.search(q, browser=target_browser)
        except Exception as e:
            logging.warning(f"[SPECTRE] Intent parse error: {e}. Executing default tab launch.")
            url = "https://google.com"
            if "http" in command:
                for word in command.split():
                    if word.startswith("http"):
                        url = word
                        break
            return await self.open_tab(url, browser=browser_type)

    async def open_tab(self, url: str, browser: str = "chrome") -> dict:
        logging.info(f"[SPECTRE] Opening tab in {browser.upper()} for: {url}")
        
        if browser.lower() == "comet":
            success = launch_desktop_comet(url)
        else:
            success = launch_desktop_chrome(url)

        if success:
            return {
                "status": "success",
                "agent": self.name,
                "action": "open_tab",
                "browser": browser,
                "url": url,
                "message": f"Opened new tab in {browser.upper()} browser: {url}"
            }
        else:
            return {"status": "error", "agent": self.name, "message": f"Failed to open tab in {browser}"}

    async def search(self, query: str, browser: str = "chrome") -> dict:
        clean_q = query.replace("search", "").replace("google", "").strip()
        encoded = urllib.parse.quote(clean_q)
        url = f"https://www.google.com/search?q={encoded}"
        return await self.open_tab(url, browser=browser)
