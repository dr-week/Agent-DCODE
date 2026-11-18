"""
Structured JSON log storage for project tracking.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from dcode.config import LOGS_DIR, MAX_LOG_ENTRIES


def ensure_logs_dir() -> None:
    """Create .logs directory if it doesn't exist."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def get_log_path(project: str) -> str:
    """Get the log file path for a project."""
    ensure_logs_dir()
    return str(LOGS_DIR / f"{project}.json")


def read_logs(project: str) -> List[Dict[str, Any]]:
    """Read all logs for a project."""
    path = LOGS_DIR / f"{project}.json"
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def write_log(
    project: str, task: str, action: str, status: str, details: str = ""
) -> Dict[str, Any]:
    """Append a new log entry to a project's log file with pruning."""
    ensure_logs_dir()
    logs = read_logs(project)
    entry = {
        "timestamp": datetime.now().isoformat(),
        "task": task,
        "action": action,
        "status": status,
        "details": details,
    }
    logs.append(entry)
    if len(logs) > MAX_LOG_ENTRIES:
        logs = logs[-MAX_LOG_ENTRIES:]
    path = LOGS_DIR / f"{project}.json"
    path.write_text(json.dumps(logs, indent=2), encoding="utf-8")
    return entry


def clear_logs(project: Optional[str] = None) -> None:
    """Clear logs for a project or all projects."""
    ensure_logs_dir()
    if project:
        path = LOGS_DIR / f"{project}.json"
        if path.exists():
            path.unlink()
    else:
        for file in LOGS_DIR.glob("*.json"):
            file.unlink()
