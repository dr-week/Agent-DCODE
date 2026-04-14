"""
Structured logging system for project tracking.
Maintains per-project JSON logs with automatic pruning to last 20 entries.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

LOGS_DIR = ".logs"
MAX_ENTRIES = 20


def ensure_logs_dir() -> None:
    """Create .logs directory if it doesn't exist."""
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)


def _get_log_path(project: str) -> str:
    """Get the log file path for a project."""
    ensure_logs_dir()
    return os.path.join(LOGS_DIR, f"{project}.json")


def write_log(project: str, task: str, action: str, status: str, details: str = "") -> Dict[str, Any]:
    """
    Append a new log entry to a project's log file.
    
    Args:
        project: Project name (e.g., "dcode", "colab_agent")
        task: Task description
        action: Action executed
        status: "success" or "fail"
        details: Additional details (optional)
    
    Returns:
        The log entry that was written.
    """
    ensure_logs_dir()
    log_path = _get_log_path(project)
    
    # Read existing logs
    logs = []
    if os.path.exists(log_path):
        try:
            with open(log_path, "r") as f:
                logs = json.load(f)
        except (json.JSONDecodeError, IOError):
            logs = []
    
    # Create new entry
    entry = {
        "timestamp": datetime.now().isoformat(),
        "task": task,
        "action": action,
        "status": status,
        "details": details
    }
    
    # Append and prune to last MAX_ENTRIES
    logs.append(entry)
    if len(logs) > MAX_ENTRIES:
        logs = logs[-MAX_ENTRIES:]
    
    # Write back
    with open(log_path, "w") as f:
        json.dump(logs, f, indent=2)
    
    return entry


def read_logs(project: str) -> List[Dict[str, Any]]:
    """
    Read all logs for a project.
    
    Args:
        project: Project name
    
    Returns:
        List of log entries, or empty list if no logs exist.
    """
    log_path = _get_log_path(project)
    
    if not os.path.exists(log_path):
        return []
    
    try:
        with open(log_path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def get_last_state(project: str) -> Optional[Dict[str, Any]]:
    """
    Get the most recent log entry for a project.
    Useful for resuming interrupted tasks.
    
    Args:
        project: Project name
    
    Returns:
        Last log entry, or None if no logs exist.
    """
    logs = read_logs(project)
    return logs[-1] if logs else None


def get_context_for_project(project: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get last N log entries for context (useful for agent resumption).
    
    Args:
        project: Project name
        limit: Number of recent entries to return
    
    Returns:
        List of recent log entries.
    """
    logs = read_logs(project)
    return logs[-limit:] if logs else []


def format_log_summary(project: str) -> str:
    """
    Format logs as a readable summary for display.
    
    Args:
        project: Project name
    
    Returns:
        Formatted string summary.
    """
    logs = read_logs(project)
    if not logs:
        return f"No logs for project: {project}"
    
    lines = [f"📋 {project} - {len(logs)} entries:"]
    for entry in logs[-5:]:  # Show last 5
        timestamp = entry.get("timestamp", "").split("T")[1][:5]  # HH:MM
        status_icon = "✅" if entry.get("status") == "success" else "❌"
        task = entry.get("task", "")[:40]
        lines.append(f"  {timestamp} {status_icon} {task}")
    
    return "\n".join(lines)


def clear_logs(project: Optional[str] = None) -> None:
    """
    Clear logs for a project or all projects.
    
    Args:
        project: Project name (if None, clears all logs in .logs/)
    """
    if project:
        log_path = _get_log_path(project)
        if os.path.exists(log_path):
            os.remove(log_path)
    else:
        if os.path.exists(LOGS_DIR):
            for file in os.listdir(LOGS_DIR):
                if file.endswith(".json"):
                    os.remove(os.path.join(LOGS_DIR, file))
