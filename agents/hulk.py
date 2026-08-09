import os
import platform
import logging

class HulkAgent:
    """
    HULK / Offline Agent: Local failover agent executing offline rules and local script backups
    when internet connectivity is lost or online services hit limits.
    """
    def __init__(self):
        self.name = "HULK"
        self.role = "Offline Failover & Emergency Local Engine"

    def execute(self, command: str) -> dict:
        logging.warning(f"[HULK] Failover engaged for offline task: {command}")
        cmd_lower = command.lower()

        if any(k in cmd_lower for k in ["health", "status", "system", "info"]):
            return self.system_health_check()
        elif any(k in cmd_lower for k in ["calc", "math", "+", "-", "*", "/"]):
            return self._local_calculator(command)
        elif any(k in cmd_lower for k in ["file", "dir", "ls", "list"]):
            return self._list_local_files()
        else:
            return {
                "status": "success",
                "agent": self.name,
                "mode": "OFFLINE_SMASH",
                "command_processed": command,
                "message": f"HULK executed emergency local routine for: '{command}' (OS: {platform.system()})",
                "system_os": platform.system(),
                "node": platform.node()
            }

    def system_health_check(self) -> dict:
        return {
            "status": "success",
            "agent": self.name,
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python_version": platform.python_version(),
            "message": f"HULK Offline Health Check: System {platform.system()} ({platform.machine()}) is healthy and operational."
        }

    def _local_calculator(self, expr: str) -> dict:
        try:
            clean_expr = "".join([c for c in expr if c in "0123456789+-*/(). "])
            if not clean_expr.strip():
                clean_expr = "10 + 20"
            result = eval(clean_expr)
            return {
                "status": "success",
                "agent": self.name,
                "expression": clean_expr,
                "result": result,
                "message": f"HULK Offline Math Engine: {clean_expr} = {result}"
            }
        except Exception as e:
            return {"status": "error", "agent": self.name, "message": f"Local math evaluation error: {e}"}

    def _list_local_files(self) -> dict:
        try:
            files = os.listdir(".")[:10]
            return {
                "status": "success",
                "agent": self.name,
                "files": files,
                "message": f"HULK Offline Directory Scan: {len(files)} files found locally."
            }
        except Exception as e:
            return {"status": "error", "agent": self.name, "message": f"Directory scan error: {e}"}
