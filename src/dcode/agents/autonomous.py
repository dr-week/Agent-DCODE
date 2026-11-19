"""
Autonomous Coding Agent Loop (Plan → Act → Verify → Iterate).
Executes iterative task resolution with real-time transparency tracking.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from dcode.agents.planner import generate_actions, generate_plan
from dcode.agents.verifier import check_goal_complete, execute_and_verify
from dcode.observability import create_new_session, write_log


class ModelType(Enum):
    LOCAL = "local"
    GEMINI = "gemini"
    OPENAI = "openai"


class AutonomousAgent:
    """Autonomous agent that loops: plan -> execute -> check -> refine."""

    def __init__(self, project_name: str = "autonomous", max_iterations: int = 10):
        self.project_name = project_name
        self.max_iterations = max_iterations
        self.iteration = 0
        self.execution_history: List[Dict[str, Any]] = []
        self.errors: List[str] = []
        self.success_criteria: Optional[str] = None

    def run(
        self, goal: str, initial_context: str = "",
        success_criteria: Optional[str] = None, model_strategy: str = "auto",
    ) -> Dict[str, Any]:
        tracker = create_new_session()
        tracker.start_execution(goal, plan_steps=["Plan", "Generate", "Execute", "Verify"])
        self.success_criteria = success_criteria or f"Goal: {goal}"
        result: Dict[str, Any] = {
            "goal": goal, "success": False, "iterations": 0,
            "final_state": None, "errors": [], "plan": [], "actions_executed": 0,
        }
        write_log(self.project_name, goal, "autonomous_start", "success", f"Max: {self.max_iterations}")

        while self.iteration < self.max_iterations:
            self.iteration += 1
            tracker.progress = int(10 + (self.iteration / self.max_iterations) * 80)
            plan = generate_plan(goal, initial_context)
            if not plan:
                self._fail(tracker, "Failed to generate plan", "Plan generation failed")
                break
            result["plan"] = plan.get("steps", [])

            actions_resp = generate_actions(goal, result["plan"], initial_context)
            if not actions_resp:
                self._fail(tracker, "Failed to generate actions", "Action generation failed")
                break
            actions = actions_resp.get("actions", [])
            result["actions_executed"] += len(actions)

            exec_res = execute_and_verify(actions)
            self.execution_history.append(exec_res)
            result["iterations"] = self.iteration

            if exec_res.get("success") and check_goal_complete(exec_res, self.success_criteria):
                result["success"], result["final_state"] = True, exec_res
                tracker.complete_execution(success=True)
                write_log(self.project_name, goal, "autonomous_complete", "success", f"Iter {self.iteration}")
                break
            if exec_res.get("error"):
                self._fail(tracker, exec_res["error"], f"Iteration {self.iteration}")
                initial_context += f"\n\nLast attempt error:\n{exec_res['error']}"

        if not result["success"] and self.iteration >= self.max_iterations:
            result["error"] = f"Max iterations ({self.max_iterations}) reached"
            tracker.complete_execution(success=False)
        result["errors"] = self.errors
        return result

    def _fail(self, tracker: Any, msg: str, ctx: str) -> None:
        self.errors.append(msg)
        tracker.add_error(msg, ctx)
        tracker.complete_step(msg, success=False)


def run_autonomous_agent(goal: str, project_name: str = "autonomous", max_iterations: int = 10, context: str = "") -> Dict[str, Any]:
    return AutonomousAgent(project_name, max_iterations).run(goal, context)
