"""
Log state queries and human-readable log formatting.
"""

from typing import Any, Dict, List, Optional
from dcode.observability.log_store import read_logs


def get_last_state(project: str) -> Optional[Dict[str, Any]]:
    """Get the most recent log entry for a project."""
    logs = read_logs(project)
    return logs[-1] if logs else None


def get_context_for_project(project: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Get last N log entries for context."""
    logs = read_logs(project)
    return logs[-limit:] if logs else []


def format_log_summary(project: str) -> str:
    """Format logs as a readable summary for display."""
    logs = read_logs(project)
    if not logs:
        return f"No logs for project: {project}"

    lines = [f"📋 {project} - {len(logs)} entries:"]
    for entry in logs[-5:]:
        ts_parts = entry.get("timestamp", "").split("T")
        timestamp = ts_parts[1][:5] if len(ts_parts) > 1 else "00:00"
        status_icon = "✅" if entry.get("status") == "success" else "❌"
        task = entry.get("task", "")[:40]
        lines.append(f"  {timestamp} {status_icon} {task}")

    return "\n".join(lines)
