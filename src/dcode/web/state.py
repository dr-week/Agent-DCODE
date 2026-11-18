"""
Shared in-memory state for Flask Web UI routes.
"""

from typing import Any, Dict, List

chat_history: List[Dict[str, str]] = []
agent_log: List[Dict[str, Any]] = []

current_file_state: Dict[str, Any] = {
    "path": None,
    "status": "pending",  # pending, working, done, error
    "message": "",
}
