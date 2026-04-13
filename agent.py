"""
Codex-like AI Coding Agent
Single-cycle flow: INPUT → PLAN → ACTION → RESULT
"""

import json
from ollama_client import ask_llm_structured
from parser import extract_json
from executor import execute_actions


class CodexAgent:
    def __init__(self):
        self.messages = []
        self.execution_log = []

    def execute_task(self, user_task: str, context: dict = None):
        """
        Execute a coding task with planning and action.
        
        Args:
            user_task: The coding task description
            context: Optional context (selected code, file content, etc.)
        
        Returns:
            dict: {plan, actions, results, success}
        """
        result = {
            "task": user_task,
            "plan": [],
            "actions": [],
            "results": [],
            "success": False,
            "error": None
        }

        # Step 1: Get plan from LLM
        plan_response = self._get_plan(user_task, context)
        if not plan_response:
            result["error"] = "Failed to generate plan"
            return result

        result["plan"] = plan_response.get("steps", [])

        # Step 2: Get structured actions from LLM
        action_response = self._get_actions(user_task, result["plan"], context)
        if not action_response:
            result["error"] = "Failed to generate actions"
            return result

        result["actions"] = action_response.get("actions", [])

        # Step 3: Execute actions
        try:
            exec_results = execute_actions(result["actions"])
            result["results"] = exec_results
            result["success"] = True
        except Exception as e:
            result["error"] = str(e)
            result["success"] = False

        self.execution_log.append(result)
        return result

    def _get_plan(self, task: str, context: dict = None) -> dict:
        """
        Generate a step-by-step plan for the task.
        Single LLM call for planning.
        """
        prompt = f"""You are an expert AI coding assistant. 
        
Task: {task}

Generate a SHORT step-by-step plan (3-5 steps) to solve this task.

Return ONLY JSON:
{{
  "steps": [
    {{"step": 1, "description": "First task"}},
    {{"step": 2, "description": "Second task"}}
  ]
}}"""

        if context:
            prompt += f"\n\nContext:\n{json.dumps(context, indent=2)}"

        response = ask_llm_structured(prompt)
        return extract_json(response)

    def _get_actions(self, task: str, plan: list, context: dict = None) -> dict:
        """
        Generate structured actions based on the plan.
        Single LLM call for action generation.
        """
        plan_text = "\n".join([f"{s['step']}. {s['description']}" for s in plan])

        prompt = f"""You are an expert AI coding assistant.

Task: {task}

Plan:
{plan_text}

Generate actions to complete this task. Return ONLY valid JSON with "actions" array.

Available actions:
- create_file: {{"type": "write_file", "path": "projects/file.py", "content": "code"}}
- edit_file: {{"type": "append_file", "path": "projects/file.py", "content": "code"}}
- read_file: {{"type": "read_file", "path": "projects/file.py"}}
- run_code: {{"type": "run_python", "code": "python code"}}
- execute_cmd: {{"type": "run_bash", "command": "shell command"}}
- list_files: {{"type": "list_files", "path": "projects", "max_depth": 2}}

Return ONLY JSON:
{{
  "actions": [
    {{"type": "write_file", "path": "projects/file.py", "content": "code"}}
  ]
}}"""

        if context:
            prompt += f"\n\nContext:\n{json.dumps(context, indent=2)}"

        response = ask_llm_structured(prompt)
        return extract_json(response)

    def get_execution_log(self):
        """Get all execution logs."""
        return self.execution_log


# Singleton instance
_agent = None


def get_agent():
    global _agent
    if _agent is None:
        _agent = CodexAgent()
    return _agent


def execute_task(task: str, context: dict = None):
    """Convenience function to execute a task."""
    return get_agent().execute_task(task, context)
