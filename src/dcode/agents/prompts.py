"""
Prompt templates for planning and action generation across Autonomous and Codex agents.
"""

from typing import Any, Dict, List


def build_plan_prompt(goal: str, context: str = "") -> str:
    """Build structured JSON prompt for step-by-step plan generation."""
    ctx_block = f"\nContext:\n{context}\n" if context else ""
    return f"""You are an expert software architect planning a coding task.

Goal: {goal}
{ctx_block}
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


def build_actions_prompt(goal: str, plan: List[Dict[str, Any]], context: str = "") -> str:
    """Build structured JSON prompt for concrete tool action generation."""
    plan_text = "\n".join(
        f"{s.get('step', i)}. {s.get('description', '')}" for i, s in enumerate(plan, 1)
    )
    ctx_block = f"\nContext:\n{context}\n" if context else ""

    return f"""You are an expert software developer generating concrete coding actions.

Goal: {goal}

Plan:
{plan_text}
{ctx_block}
Available actions:
- write_file: {{"type": "write_file", "path": "projects/file.py", "content": "code"}}
- replace_in_file: {{"type": "replace_in_file", "path": "projects/file.py", "target": "old", "replacement": "new"}}
- append_file: {{"type": "append_file", "path": "projects/file.py", "content": "code"}}
- read_file: {{"type": "read_file", "path": "projects/file.py"}}
- search_code: {{"type": "search_code", "pattern": "def ", "path": "projects"}}
- run_python: {{"type": "run_python", "code": "python code"}}
- run_bash: {{"type": "run_bash", "command": "bash command"}}
- list_files: {{"type": "list_files", "path": "projects"}}

Return ONLY JSON:
{{
  "actions": [
    {{"type": "write_file", "path": "projects/main.py", "content": "print('hello')"}}
  ],
  "reasoning": "Why these actions progress toward goal"
}}"""
