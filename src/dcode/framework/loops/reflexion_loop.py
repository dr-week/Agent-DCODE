"""
Reflexion Cognitive Loop (Actor ↔ Critic self-refinement cycle).
Generates a candidate solution, critiques it against quality criteria, and refines.
"""

from typing import Any, Callable, Dict, Optional
from dcode.framework.core.spec import AgentSpec
from dcode.llm.ollama_client import ask_llm_structured
from dcode.llm.parser import extract_json


class ReflexionAgent:
    """Actor-Critic self-refinement agent loop."""

    def __init__(self, spec: AgentSpec, llm_fn: Optional[Callable[[str], str]] = None):
        self.spec = spec
        self.llm_fn = llm_fn or ask_llm_structured

    def _generate_draft(self, task: str, feedback: str) -> str:
        prompt = (
            f"{self.spec.build_system_instructions()}\n"
            f"Task: {task}\n"
            f"Prior Critic Feedback: {feedback or 'None'}\n"
            'Return ONLY JSON: {"draft": "complete solution"}'
        )
        data = extract_json(self.llm_fn(prompt)) or {}
        return str(data.get("draft", ""))

    def _critique_draft(self, task: str, draft: str) -> Dict[str, Any]:
        prompt = (
            f"You are a strict QA Critic reviewing output for task: {task}\n"
            f"Candidate Draft:\n{draft}\n"
            'Return ONLY JSON: {"approved": true, "score": 9, "feedback": "specific improvements"}'
        )
        return extract_json(self.llm_fn(prompt)) or {"approved": False, "feedback": "Invalid critique"}

    def run(self, task: str) -> Dict[str, Any]:
        feedback = ""
        history = []

        for iteration in range(1, self.spec.max_iterations + 1):
            draft = self._generate_draft(task, feedback)
            critique = self._critique_draft(task, draft)
            approved = bool(critique.get("approved", False))
            feedback = str(critique.get("feedback", ""))

            history.append({
                "iteration": iteration,
                "draft": draft,
                "approved": approved,
                "score": critique.get("score", 0),
                "feedback": feedback,
            })
            if approved:
                return {
                    "success": True,
                    "agent": self.spec.name,
                    "final_output": draft,
                    "iterations": iteration,
                    "history": history,
                }

        return {
            "success": False,
            "agent": self.spec.name,
            "final_output": history[-1]["draft"] if history else "",
            "iterations": len(history),
            "history": history,
        }
