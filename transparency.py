"""
Real-time agent transparency tracker.
Tracks plan, actions, status, progress, and errors for streaming to UI.
"""

import time
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


class TransparencyTracker:
    """
    Tracks agent execution transparently for real-time UI updates.
    """

    def __init__(self, session_id: str = None):
        self.session_id = session_id or f"session_{int(time.time())}"
        self.lock = threading.Lock()
        
        # Core state
        self.plan = []
        self.actions = []
        self.errors = []
        self.current_step = None
        self.status = "idle"
        self.progress = 0
        self.estimated_time = 0
        self.start_time = None
        self.end_time = None
        
    def start_execution(self, task: str, plan_steps: List[str] = None):
        """Start tracking new execution"""
        with self.lock:
            self.start_time = datetime.now()
            self.end_time = None
            self.status = "planning"
            self.progress = 0
            self.errors = []
            self.actions = []
            self.plan = plan_steps or []
            self.current_step = None
    
    def add_plan(self, steps: List[str], estimated_time: int = 0):
        """Add plan steps"""
        with self.lock:
            self.plan = steps
            self.estimated_time = estimated_time
            self.status = "planned"
            self.progress = 10
    
    def start_step(self, step_index: int, step_name: str):
        """Mark step as running"""
        with self.lock:
            self.status = f"executing_step_{step_index}"
            self.current_step = {
                "index": step_index,
                "name": step_name,
                "status": "running",
                "start_time": datetime.now().isoformat(),
                "output": ""
            }
            # Calculate progress
            if self.plan:
                self.progress = 10 + int((step_index / len(self.plan)) * 80)
    
    def add_action(self, action: Dict[str, Any]):
        """Record action execution"""
        with self.lock:
            action_record = {
                "timestamp": datetime.now().isoformat(),
                "type": action.get("type", "unknown"),
                "description": action.get("description", ""),
                "status": "executing",
                "output": action.get("output", ""),
                "success": action.get("success", None)
            }
            self.actions.append(action_record)
    
    def complete_action(self, action_index: int, output: str, success: bool = True):
        """Mark action as complete"""
        with self.lock:
            if action_index < len(self.actions):
                self.actions[action_index]["status"] = "completed"
                self.actions[action_index]["output"] = output
                self.actions[action_index]["success"] = success
                if not success:
                    self.actions[action_index]["status"] = "error"
    
    def complete_step(self, output: str = "", success: bool = True):
        """Mark current step as complete"""
        with self.lock:
            if self.current_step:
                self.current_step["status"] = "completed" if success else "error"
                self.current_step["end_time"] = datetime.now().isoformat()
                self.current_step["output"] = output
    
    def add_error(self, error: str, context: str = ""):
        """Record error"""
        with self.lock:
            self.errors.append({
                "timestamp": datetime.now().isoformat(),
                "message": error,
                "context": context,
                "step": self.current_step["name"] if self.current_step else "unknown"
            })
            self.status = "error"
    
    def complete_execution(self, success: bool = True):
        """Mark execution as complete"""
        with self.lock:
            self.end_time = datetime.now()
            self.status = "completed" if success else "failed"
            self.progress = 100
    
    def get_state(self) -> Dict[str, Any]:
        """Get current state for UI"""
        with self.lock:
            elapsed_time = 0
            if self.start_time:
                end = self.end_time or datetime.now()
                elapsed_time = int((end - self.start_time).total_seconds())
            
            return {
                "session_id": self.session_id,
                "plan": self.plan,
                "current_step": self.current_step,
                "actions": self.actions,
                "status": self.status,
                "progress": self.progress,
                "estimated_time": self.estimated_time,
                "elapsed_time": elapsed_time,
                "errors": self.errors,
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": self.end_time.isoformat() if self.end_time else None,
            }


# Global tracker instance
_current_tracker: Optional[TransparencyTracker] = None
_tracker_lock = threading.Lock()


def get_tracker() -> TransparencyTracker:
    """Get or create current tracker"""
    global _current_tracker
    if _current_tracker is None:
        with _tracker_lock:
            if _current_tracker is None:
                _current_tracker = TransparencyTracker()
    return _current_tracker


def create_new_session() -> TransparencyTracker:
    """Create new tracking session"""
    global _current_tracker
    with _tracker_lock:
        _current_tracker = TransparencyTracker()
        return _current_tracker


def reset_tracker():
    """Reset tracker (for cleanup)"""
    global _current_tracker
    with _tracker_lock:
        _current_tracker = None
