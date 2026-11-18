"""
Real-time agent transparency tracker class.
"""

from datetime import datetime
from enum import Enum
import threading
import time
from typing import Any, Dict, List, Optional


class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


class TransparencyTracker:
    """Tracks agent execution transparently for real-time UI updates."""

    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or f"session_{int(time.time())}"
        self.lock = threading.Lock()
        self.plan: List[str] = []
        self.actions: List[Dict[str, Any]] = []
        self.errors: List[Dict[str, Any]] = []
        self.current_step: Optional[Dict[str, Any]] = None
        self.status = "idle"
        self.progress = 0
        self.estimated_time = 0
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

    def start_execution(self, task: str, plan_steps: Optional[List[str]] = None) -> None:
        with self.lock:
            self.start_time, self.end_time = datetime.now(), None
            self.status, self.progress = "planning", 0
            self.errors, self.actions = [], []
            self.plan, self.current_step = plan_steps or [], None

    def add_plan(self, steps: List[str], estimated_time: int = 0) -> None:
        with self.lock:
            self.plan, self.estimated_time = steps, estimated_time
            self.status, self.progress = "planned", 10

    def start_step(self, step_index: int, step_name: str) -> None:
        with self.lock:
            self.status = f"executing_step_{step_index}"
            self.current_step = {
                "index": step_index, "name": step_name,
                "status": "running", "start_time": datetime.now().isoformat(), "output": "",
            }
            if self.plan:
                self.progress = 10 + int((step_index / len(self.plan)) * 80)

    def add_action(self, action: Dict[str, Any]) -> None:
        with self.lock:
            self.actions.append({
                "timestamp": datetime.now().isoformat(), "type": action.get("type", "unknown"),
                "description": action.get("description", ""), "status": "executing",
                "output": action.get("output", ""), "success": action.get("success", None),
            })

    def complete_action(self, action_index: int, output: str, success: bool = True) -> None:
        with self.lock:
            if action_index < len(self.actions):
                self.actions[action_index].update({"status": "completed" if success else "error", "output": output, "success": success})

    def complete_step(self, output: str = "", success: bool = True) -> None:
        with self.lock:
            if self.current_step:
                self.current_step.update({"status": "completed" if success else "error", "end_time": datetime.now().isoformat(), "output": output})

    def add_error(self, error: str, context: str = "") -> None:
        with self.lock:
            step = self.current_step["name"] if self.current_step else "unknown"
            self.errors.append({"timestamp": datetime.now().isoformat(), "message": error, "context": context, "step": step})
            self.status = "error"

    def complete_execution(self, success: bool = True) -> None:
        with self.lock:
            self.end_time, self.status, self.progress = datetime.now(), ("completed" if success else "failed"), 100

    def get_state(self) -> Dict[str, Any]:
        with self.lock:
            elapsed = int(((self.end_time or datetime.now()) - self.start_time).total_seconds()) if self.start_time else 0
            return {
                "session_id": self.session_id, "plan": self.plan, "current_step": self.current_step,
                "actions": self.actions, "status": self.status, "progress": self.progress,
                "estimated_time": self.estimated_time, "elapsed_time": elapsed, "errors": self.errors,
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": self.end_time.isoformat() if self.end_time else None,
            }
