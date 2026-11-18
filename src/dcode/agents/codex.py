"""
Codex-like Single-Cycle AI Coding Agent (INPUT → PLAN → ACTION → RESULT).
"""

from typing import Any, Dict, List, Optional
from dcode.agents.planner import generate_actions, generate_plan
from dcode.agents.verifier import execute_and_verify
from dcode.observability import write_log


class CodexAgent:
    """Single-cycle agent executing Plan → Action → Result."""

    def __init__(self) -> None:
        self.messages: List[Dict[str, str]] = []
        self.execution_log: List[Dict[str, Any]] = []

    def execute_task(self, user_task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "task": user_task,
            "plan": [],
            "actions": [],
            "results": [],
            "success": False,
            "error": None,
        }

        plan_response = generate_plan(user_task, context)
        if not plan_response:
            result["error"] = "Failed to generate plan"
            return result

        result["plan"] = plan_response.get("steps", [])

        action_response = generate_actions(user_task, result["plan"], context)
        if not action_response:
            result["error"] = "Failed to generate actions"
            return result

        result["actions"] = action_response.get("actions", [])

        exec_check = execute_and_verify(result["actions"])
        result["results"] = exec_check.get("outputs", [])
        result["success"] = exec_check.get("success", False)
        result["error"] = exec_check.get("error")

        status = "success" if result["success"] else "fail"
        action_summary = f"{len(result['actions'])} actions"
        details = result["error"] or f"Executed {action_summary}"
        write_log("agent", user_task, action_summary, status, details)

        self.execution_log.append(result)
        return result

    def get_execution_log(self) -> List[Dict[str, Any]]:
        return self.execution_log


_agent: Optional[CodexAgent] = None


def get_agent() -> CodexAgent:
    global _agent
    if _agent is None:
        _agent = CodexAgent()
    return _agent


def execute_task(task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return get_agent().execute_task(task, context)
