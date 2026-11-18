"""
Autonomous Coding Agent Loop (Plan → Act → Verify → Iterate).
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
    """Autonomous agent that loops: plan → execute → check → refine."""

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

            tracker.start_step(0, f"Plan - Iteration {self.iteration}")
            plan = generate_plan(goal, initial_context)
            if not plan:
                self._fail_step(tracker, "Failed to generate plan", "Plan generation failed")
                break
            result["plan"] = plan.get("steps", [])
            tracker.complete_step(f"Generated {len(result['plan'])} plan steps")
            tracker.add_plan([s.get("description", f"Step {i+1}") for i, s in enumerate(result["plan"])], 300)

            tracker.start_step(1, f"Generate Actions - Iteration {self.iteration}")
            actions_resp = generate_actions(goal, result["plan"], initial_context)
            if not actions_resp:
                self._fail_step(tracker, "Failed to generate actions", "Action generation failed")
                break
            action_list = actions_resp.get("actions", [])
            result["actions_executed"] += len(action_list)
            tracker.complete_step(f"Generated {len(action_list)} actions")

            tracker.start_step(2, f"Execute Actions - Iteration {self.iteration}")
            for i, act in enumerate(action_list):
                tracker.add_action({"type": act.get("type", "unknown"), "description": f"Action {i+1}"})
            exec_res = execute_and_verify(action_list)
            self.execution_history.append(exec_res)
            for i, out in enumerate(exec_res.get("outputs", [])):
                tracker.complete_action(i, str(out), success=exec_res.get("success", True))

            tracker.start_step(3, f"Verify - Iteration {self.iteration}")
            result["iterations"] = self.iteration
            if exec_res.get("success") and check_goal_complete(exec_res, self.success_criteria):
                result["success"], result["final_state"] = True, exec_res
                tracker.complete_step("Goal verified and complete!", success=True)
                tracker.complete_execution(success=True)
                write_log(self.project_name, goal, "autonomous_complete", "success", f"Iter {self.iteration}")
                break
            if exec_res.get("error"):
                self._fail_step(tracker, exec_res["error"], f"Iteration {self.iteration}")
                initial_context += f"\n\nLast attempt error:\n{exec_res['error']}"

        if not result["success"] and self.iteration >= self.max_iterations:
            result["error"] = f"Max iterations ({self.max_iterations}) reached"
            tracker.complete_execution(success=False)
        result["errors"] = self.errors
        return result

    def _fail_step(self, tracker: Any, msg: str, ctx: str) -> None:
        self.errors.append(msg)
        tracker.add_error(msg, ctx)
        tracker.complete_step(msg, success=False)


def run_autonomous_agent(goal: str, project_name: str = "autonomous", max_iterations: int = 10, context: str = "") -> Dict[str, Any]:
    return AutonomousAgent(project_name, max_iterations).run(goal, context)
