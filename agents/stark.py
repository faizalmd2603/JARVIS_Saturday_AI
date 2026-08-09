import os
import sys
import time
import json
import glob
import logging
import subprocess
import pyautogui
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from api_router import router

pyautogui.FAILSAFE = False

REGISTRY_CACHE_FILE = "system_apps_registry.json"
user_profile = os.environ.get("USERPROFILE", r"C:\Users\Default")

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(CHROME_EXE):
    CHROME_EXE = os.path.join(user_profile, r"AppData\Local\Google\Chrome\Application\chrome.exe")

COMET_EXE = os.path.join(user_profile, r"AppData\Local\Perplexity\Comet\Application\comet.exe")

class SystemAppCrawler:
    """
    Deep Windows System App Crawler:
    Scans Start Menu, Desktop, Taskbar, Program Files, AppData, System32 EXEs, and Web Apps.
    """
    def __init__(self):
        self.app_index: Dict[str, Dict[str, str]] = {}
        self.load_or_crawl()

    def load_or_crawl(self):
        if os.path.exists(REGISTRY_CACHE_FILE):
            try:
                with open(REGISTRY_CACHE_FILE, "r", encoding="utf-8") as f:
                    self.app_index = json.load(f)
                
                # Custom app override guarantees
                self.app_index["youtube"] = {"title": "YouTube Web App", "path": "https://www.youtube.com", "type": "youtube_app"}
                self.app_index["youtube app"] = {"title": "YouTube Web App", "path": "https://www.youtube.com", "type": "youtube_app"}
                self.app_index["comet"] = {"title": "Comet Browser", "path": COMET_EXE, "type": "comet_exe"}
                self.app_index["comet browser"] = {"title": "Comet Browser", "path": COMET_EXE, "type": "comet_exe"}
                self.app_index["whatsapp"] = {"title": "WhatsApp", "path": "whatsapp:", "type": "whatsapp_app"}
                
                logging.info(f"[SystemAppCrawler] Loaded {len(self.app_index)} indexed apps from cache.")
                return
            except Exception as e:
                logging.warning(f"[SystemAppCrawler] Could not read cache: {e}. Crawling system...")
        
        self.crawl_system_apps()

    def crawl_system_apps(self):
        logging.info("[SystemAppCrawler] Deep scanning Windows installed applications & shortcuts...")
        new_index = {}

        scan_dirs = [
            r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
            os.path.join(user_profile, r"AppData\Roaming\Microsoft\Windows\Start Menu\Programs"),
            os.path.join(user_profile, "Desktop"),
            r"C:\Users\Public\Desktop",
            os.path.join(user_profile, r"AppData\Roaming\Microsoft\Internet Explorer\Quick Launch\User Pinned\TaskBar"),
            os.path.join(user_profile, r"AppData\Local\Programs")
        ]

        for base_dir in scan_dirs:
            if not os.path.exists(base_dir):
                continue
            
            for root, dirs, files in os.walk(base_dir):
                depth = root[len(base_dir):].count(os.sep)
                if depth > 3:
                    dirs.clear()
                    continue

                for f in files:
                    ext = os.path.splitext(f)[1].lower()
                    if ext in [".lnk", ".url", ".exe"]:
                        full_path = os.path.join(root, f)
                        raw_name = os.path.splitext(f)[0]
                        clean_name = raw_name.lower().replace("shortcut", "").replace("-", " ").strip()
                        
                        if clean_name and clean_name not in new_index:
                            new_index[clean_name] = {
                                "title": raw_name,
                                "path": full_path,
                                "type": "shortcut" if ext in [".lnk", ".url"] else "exe"
                            }

        # Program Files EXEs
        pf_patterns = [
            r"C:\Program Files\*\*.exe",
            r"C:\Program Files (x86)\*\*.exe"
        ]
        for pattern in pf_patterns:
            for exe_file in glob.glob(pattern):
                raw_name = os.path.splitext(os.path.basename(exe_file))[0]
                clean_name = raw_name.lower().strip()
                if clean_name and clean_name not in new_index and not clean_name.startswith("unins"):
                    new_index[clean_name] = {
                        "title": raw_name,
                        "path": exe_file,
                        "type": "exe"
                    }

        # Override & Core Aliases
        known_protocols = {
            "youtube": {"title": "YouTube Web App", "path": "https://www.youtube.com", "type": "youtube_app"},
            "youtube app": {"title": "YouTube Web App", "path": "https://www.youtube.com", "type": "youtube_app"},
            "comet": {"title": "Comet Browser", "path": COMET_EXE, "type": "comet_exe"},
            "comet browser": {"title": "Comet Browser", "path": COMET_EXE, "type": "comet_exe"},
            "whatsapp": {"title": "WhatsApp", "path": "whatsapp:", "type": "whatsapp_app"},
            "spotify": {"title": "Spotify", "path": "spotify:", "type": "protocol"},
            "calculator": {"title": "Calculator", "path": "calc", "type": "cmd"},
            "calc": {"title": "Calculator", "path": "calc", "type": "cmd"},
            "notepad": {"title": "Notepad", "path": "notepad", "type": "cmd"},
            "chrome": {"title": "Google Chrome", "path": "chrome", "type": "cmd"},
            "edge": {"title": "Microsoft Edge", "path": "msedge", "type": "cmd"},
            "explorer": {"title": "File Explorer", "path": "explorer", "type": "cmd"},
            "paint": {"title": "Paint", "path": "mspaint", "type": "cmd"},
            "cmd": {"title": "Command Prompt", "path": "cmd", "type": "cmd"},
            "powershell": {"title": "PowerShell", "path": "powershell", "type": "cmd"},
            "task manager": {"title": "Task Manager", "path": "taskmgr", "type": "cmd"},
            "settings": {"title": "Settings", "path": "ms-settings:", "type": "protocol"}
        }

        for alias, data in known_protocols.items():
            new_index[alias] = data

        self.app_index = new_index
        try:
            with open(REGISTRY_CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.app_index, f, indent=2)
            logging.info(f"[SystemAppCrawler] Crawl complete. Indexed {len(self.app_index)} apps to {REGISTRY_CACHE_FILE}.")
        except Exception as e:
            logging.error(f"[SystemAppCrawler] Failed to save registry cache: {e}")

    def find_app(self, query: str) -> Optional[Tuple[str, Dict[str, str]]]:
        q = query.lower().strip()
        
        # 1. Exact match
        if q in self.app_index:
            return q, self.app_index[q]

        # 2. Substring match
        matches = []
        for key, val in self.app_index.items():
            if q in key or key in q:
                matches.append((key, val))
        
        if matches:
            matches.sort(key=lambda x: len(x[0]))
            return matches[0]

        return None

class StarkAgent:
    """
    STARK / OS Agent: Desktop & Taskbar automation using Deep System App Crawler, pyautogui, and subprocess.
    Launches installed desktop apps (YouTube Web App, Comet Browser, WhatsApp, VS Code, Chrome, VLC, Notepad, Calc, Spotify),
    taskbar apps via Win+Number, and manages active OS windows.
    """
    def __init__(self):
        self.name = "STARK"
        self.role = "OS & Desktop System App Crawler Specialist"
        self.crawler = SystemAppCrawler()

    def execute(self, command: str) -> dict:
        cmd_lower = command.lower()

        # Re-crawl system index command
        if "crawl" in cmd_lower or "rescan apps" in cmd_lower or "refresh apps" in cmd_lower:
            self.crawler.crawl_system_apps()
            return {
                "status": "success",
                "agent": self.name,
                "action": "crawl_apps",
                "message": f"Deep crawler rescan complete. Indexed {len(self.crawler.app_index)} applications."
            }

        # Taskbar Slot Launch (e.g., "taskbar 1", "slot 2", "win 3")
        if "taskbar" in cmd_lower or "slot" in cmd_lower:
            digits = [int(c) for c in command if c.isdigit()]
            slot = digits[0] if digits else 1
            return self.launch_taskbar_app(slot)

        # Window Switch (Alt+Tab)
        if "switch" in cmd_lower or "alt tab" in cmd_lower:
            return self.switch_window()

        # Extract app name
        app_name = command
        for prefix in ["launch app ", "open app ", "launch ", "open ", "run "]:
            if cmd_lower.startswith(prefix):
                app_name = command[len(prefix):].strip()
                break

        return self.open_installed_app(app_name)

    def launch_taskbar_app(self, slot_index: int = 1) -> dict:
        """Launches app pinned at taskbar slot Win + [1..9]"""
        try:
            slot_index = max(1, min(9, int(slot_index)))
            logging.info(f"[STARK] Pressing Win+{slot_index} for taskbar slot launch...")
            pyautogui.keyDown('win')
            pyautogui.press(str(slot_index))
            pyautogui.keyUp('win')
            return {
                "status": "success",
                "agent": self.name,
                "action": "taskbar_launch",
                "slot": slot_index,
                "message": f"Triggered desktop taskbar app at slot Win+{slot_index}."
            }
        except Exception as e:
            return {"status": "error", "agent": self.name, "message": f"Taskbar launch failed: {e}"}

    def switch_window(self) -> dict:
        """Triggers Alt+Tab window switch"""
        try:
            pyautogui.hotkey('alt', 'tab')
            return {
                "status": "success",
                "agent": self.name,
                "action": "switch_window",
                "message": "Switched active desktop window (Alt+Tab)."
            }
        except Exception as e:
            return {"status": "error", "agent": self.name, "message": f"Window switch failed: {e}"}

    def open_installed_app(self, app_name: str) -> dict:
        """
        Deep System App Launcher.
        Searches system registry index for matching .lnk shortcuts, .exe paths, protocols, or Web App URLs.
        """
        clean_name = app_name.strip()
        logging.info(f"[STARK] Searching deep system registry for application: '{clean_name}'")

        match = self.crawler.find_app(clean_name)
        if match:
            key_name, app_info = match
            app_title = app_info["title"]
            app_path = app_info["path"]
            app_type = app_info["type"]

            logging.info(f"[STARK] Found match: '{app_title}' ({app_type}) -> {app_path}")

            try:
                if app_type == "youtube_app":
                    if os.path.exists(CHROME_EXE):
                        subprocess.Popen([CHROME_EXE, "--app=https://www.youtube.com"])
                    else:
                        os.system('cmd /c start "" "https://www.youtube.com"')
                elif app_type == "comet_exe":
                    if os.path.exists(COMET_EXE):
                        subprocess.Popen([COMET_EXE])
                    else:
                        os.system(f'cmd /c start "" "{app_path}"')
                elif app_type == "whatsapp_app":
                    os.system('cmd /c start whatsapp:')
                elif app_type in ["shortcut", "protocol", "url"]:
                    os.system(f'cmd /c start "" "{app_path}"')
                elif app_type == "cmd":
                    subprocess.Popen(f'start {app_path}', shell=True)
                else:
                    subprocess.Popen(f'"{app_path}"', shell=True)

                return {
                    "status": "success",
                    "agent": self.name,
                    "action": "open_app_indexed",
                    "app": app_title,
                    "path": app_path,
                    "message": f"Launched desktop app '{app_title}' from system registry."
                }
            except Exception as e:
                logging.warning(f"[STARK] Direct start failed for '{app_path}': {e}. Trying shell execute...")
                try:
                    os.system(f'cmd /c start "" "{app_path}"')
                    return {
                        "status": "success",
                        "agent": self.name,
                        "action": "open_app_shell",
                        "app": app_title,
                        "message": f"Launched desktop app '{app_title}' via Windows Shell."
                    }
                except Exception:
                    pass

        # Fallback: Windows Start Menu Search & Launch
        try:
            logging.info(f"[STARK] App '{clean_name}' not found in direct index. Executing Windows Start Menu Search...")
            pyautogui.press('win')
            time.sleep(0.3)
            pyautogui.write(clean_name, interval=0.04)
            time.sleep(0.4)
            pyautogui.press('enter')
            return {
                "status": "success",
                "agent": self.name,
                "action": "open_app_startmenu",
                "app": clean_name,
                "message": f"Launched desktop app '{clean_name}' via Windows Start Menu."
            }
        except Exception as e:
            return {"status": "error", "agent": self.name, "message": f"Failed to launch app '{clean_name}': {e}"}
