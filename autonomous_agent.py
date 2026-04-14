"""
Autonomous Coding Agent Loop
Continuously generates, executes, and refines code until goal is complete.
"""

import json
import os
import re
from typing import Dict, List, Optional, Any
from enum import Enum
from ollama_client import ask_llm_structured
from parser import extract_json
from executor import execute_actions
from logger import write_log, get_last_state, read_logs


class ModelType(Enum):
    LOCAL = "local"
    GEMINI = "gemini"
    OPENAI = "openai"


class AutonomousAgent:
    """
    Autonomous agent that loops: plan → execute → check → refine
    """

    def __init__(self, project_name: str = "autonomous", max_iterations: int = 10):
        self.project_name = project_name
        self.max_iterations = max_iterations
        self.iteration = 0
        self.execution_history = []
        self.errors = []
        self.success_criteria = None

    def run(
        self,
        goal: str,
        initial_context: str = "",
        success_criteria: Optional[str] = None,
        model_strategy: str = "auto"
    ) -> Dict[str, Any]:
        """
        Run autonomous agent loop until goal is complete.

        Args:
            goal: High-level goal / requirement
            initial_context: Optional context (existing code, requirements)
            success_criteria: How to verify success (e.g., "project runs without errors")
            model_strategy: "auto" (route by task), "local", "gemini", "openai"

        Returns:
            dict with final_state, iterations, success, result
        """
        self.success_criteria = success_criteria or f"Goal: {goal}"
        result = {
            "goal": goal,
            "success": False,
            "iterations": 0,
            "final_state": None,
            "errors": [],
            "plan": [],
            "actions_executed": 0,
        }

        write_log(
            self.project_name,
            goal,
            "autonomous_start",
            "success",
            f"Max iterations: {self.max_iterations}"
        )

        while self.iteration < self.max_iterations:
            self.iteration += 1
            print(f"\n🔄 [Iteration {self.iteration}/{self.max_iterations}]")

            # Step 1: Plan next steps
            plan = self._get_plan(goal, initial_context)
            if not plan:
                self.errors.append("Failed to generate plan")
                break

            result["plan"] = plan.get("steps", [])
            print(f"📋 Plan: {len(result['plan'])} steps")

            # Step 2: Generate actions
            actions = self._get_actions(goal, result["plan"], initial_context)
            if not actions:
                self.errors.append("Failed to generate actions")
                break

            num_actions = len(actions.get("actions", []))
            result["actions_executed"] += num_actions
            print(f"⚙️  Actions: {num_actions} to execute")

            # Step 3: Execute actions
            try:
                execution_result = self._execute_and_check(actions.get("actions", []))
                self.execution_history.append(execution_result)

                # Step 4: Check completion
                if execution_result.get("success") and self._check_goal_complete(execution_result):
                    result["success"] = True
                    result["final_state"] = execution_result
                    print(f"✅ Goal completed at iteration {self.iteration}")
                    write_log(
                        self.project_name,
                        goal,
                        "autonomous_complete",
                        "success",
                        f"Completed in {self.iteration} iterations"
                    )
                    break

                # Step 5: Log and continue
                if execution_result.get("error"):
                    self.errors.append(execution_result["error"])
                    print(f"⚠️  Error: {execution_result['error']}")
                    # Continue loop to retry/fix
                    initial_context += f"\n\nLast attempt error:\n{execution_result['error']}"

            except Exception as e:
                self.errors.append(str(e))
                print(f"❌ Execution error: {e}")
                break

            result["iterations"] = self.iteration

        if not result["success"] and self.iteration >= self.max_iterations:
            result["error"] = f"Max iterations ({self.max_iterations}) reached"
            write_log(
                self.project_name,
                goal,
                "autonomous_max_iterations",
                "fail",
                f"Did not complete after {self.max_iterations} iterations"
            )

        result["errors"] = self.errors
        return result

    def _get_plan(self, goal: str, context: str) -> Optional[Dict[str, Any]]:
        """Get plan from LLM (use Gemini for reasoning if available)"""
        prompt = f"""You are an expert software architect planning a coding task.

Goal: {goal}

{f"Context: {context}" if context else ""}

Create a HIGH-LEVEL plan with 3-5 main steps to achieve this goal.
Each step should be actionable and build on the previous.

Return ONLY JSON:
{{
  "steps": [
    {{"step": 1, "description": "First task"}},
    {{"step": 2, "description": "Second task"}}
  ],
  "notes": "Any important considerations"
}}"""

        try:
            response = ask_llm_structured(prompt)
            data = extract_json(response)
            return data if data and "steps" in data else None
        except Exception as e:
            print(f"[Plan] Error: {e}")
            return None

    def _get_actions(self, goal: str, plan: List[Dict], context: str) -> Optional[Dict[str, Any]]:
        """Generate concrete actions based on plan"""
        plan_text = "\n".join([f"{s.get('step', i)}. {s.get('description', '')}" for i, s in enumerate(plan, 1)])

        prompt = f"""You are an expert software developer generating concrete coding actions.

Goal: {goal}

Plan:
{plan_text}

{f"Context: {context}" if context else ""}

Generate specific actions to execute the next step of the plan.

Available actions:
- write_file: {{"type": "write_file", "path": "projects/file.py", "content": "code"}}
- append_file: {{"type": "append_file", "path": "projects/file.py", "content": "code"}}
- read_file: {{"type": "read_file", "path": "projects/file.py"}}
- run_python: {{"type": "run_python", "code": "python code"}}
- run_bash: {{"type": "run_bash", "command": "bash command"}}
- list_files: {{"type": "list_files", "path": "projects"}}

Choose 1-3 actions to make measurable progress.

Return ONLY JSON:
{{
  "actions": [
    {{"type": "write_file", "path": "projects/main.py", "content": "print('hello')"}}
  ],
  "reasoning": "Why these actions will progress toward goal"
}}"""

        try:
            response = ask_llm_structured(prompt)
            data = extract_json(response)
            return data if data and "actions" in data else None
        except Exception as e:
            print(f"[Actions] Error: {e}")
            return None

    def _execute_and_check(self, actions: List[Dict]) -> Dict[str, Any]:
        """Execute actions and check for errors"""
        result = {
            "success": True,
            "actions_count": len(actions),
            "outputs": [],
            "error": None
        }

        try:
            exec_results = execute_actions(actions)
            result["outputs"] = exec_results

            # Check for errors in output
            all_output = str(exec_results)
            if any(err in all_output.lower() for err in ["error", "failed", "traceback", "exception"]):
                result["success"] = False
                result["error"] = f"Errors detected in output: {all_output[:200]}"

        except Exception as e:
            result["success"] = False
            result["error"] = str(e)

        return result

    def _check_goal_complete(self, execution_result: Dict) -> bool:
        """Check if goal is complete based on criteria"""
        if not self.success_criteria:
            return execution_result.get("success", False)

        # Simple check: if no errors and criteria mentions core success words
        output = "\n".join([str(o) for o in execution_result.get("outputs", [])])
        success_indicators = ["success", "complete", "done", "ready", "working", "✅"]

        for indicator in success_indicators:
            if indicator.lower() in output.lower():
                return True

        # Also check: project actually runs without error
        if "error" not in output.lower() and execution_result.get("success"):
            return True

        return False


def run_autonomous_agent(
    goal: str,
    project_name: str = "autonomous",
    max_iterations: int = 10,
    context: str = ""
) -> Dict[str, Any]:
    """
    Convenience function to run autonomous agent.

    Example:
        result = run_autonomous_agent(
            goal="Create a Python function that calculates fibonacci",
            project_name="fibonacci_task",
            max_iterations=5
        )
        print(result["success"])
    """
    agent = AutonomousAgent(project_name, max_iterations)
    return agent.run(goal, context)
