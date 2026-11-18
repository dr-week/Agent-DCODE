"""
Human-in-the-Loop (HITL) approval gate for high-impact agent actions.
"""

from typing import Any, Callable, Dict, List

HIGH_RISK_ACTION_TYPES = {"run_bash", "run_command", "execute_cmd"}


class ApprovalGate:
    """Manages pending and approved high-risk actions for Human-in-the-Loop workflows."""

    def __init__(self, auto_approve: bool = False):
        self.auto_approve = auto_approve
        self.pending_queue: List[Dict[str, Any]] = []

    def requires_approval(self, action: Dict[str, Any]) -> bool:
        if self.auto_approve:
            return False
        return action.get("type") in HIGH_RISK_ACTION_TYPES

    def request_approval(
        self, action: Dict[str, Any], callback: Callable[[Dict[str, Any]], bool] = None
    ) -> bool:
        if not self.requires_approval(action):
            return True
        if callback is not None:
            return bool(callback(action))
        self.pending_queue.append(action)
        return False
