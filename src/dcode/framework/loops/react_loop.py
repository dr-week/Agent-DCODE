"""
ReAct Cognitive Loop (Reason + Act: Thought → Tool Call → Observation → Answer).
Works with any AgentSpec, custom @tool definitions, or built-in sandboxed actions.
"""

import json
from typing import Any, Callable, Dict, Optional
from dcode.framework.core.spec import AgentSpec
from dcode.framework.core.tool_decorator import ToolDefinition
from dcode.llm.ollama_client import ask_llm_structured
from dcode.llm.parser import extract_json
from dcode.tools.executor import execute_actions


class ReActAgent:
    """Executes the ReAct (Reason + Act) loop for any configured AgentSpec."""

    def __init__(self, spec: AgentSpec, llm_fn: Optional[Callable[[str], str]] = None):
        self.spec = spec
        self.llm_fn = llm_fn or ask_llm_structured
        self.tool_map: Dict[str, ToolDefinition] = {
            t.name: t for t in spec.tools if isinstance(t, ToolDefinition)
        }

    def _build_prompt(self, task: str, scratchpad: str) -> str:
        tools_desc = json.dumps([t.to_dict() for t in self.tool_map.values()], indent=2)
        return (
            f"{self.spec.build_system_instructions()}\n\n"
            f"Registered Custom Tools:\n{tools_desc}\n\n"
            f"Task: {task}\n"
            f"History / Scratchpad:\n{scratchpad or 'None'}\n\n"
            "Return ONLY JSON:\n"
            '{"thought": "reasoning", "tool": "tool_name_or_none", '
            '"tool_args": {}, "actions": [], "final_answer": "answer_when_done"}'
        )

    def run(self, task: str) -> Dict[str, Any]:
        scratchpad = ""
        trace = []

        for step in range(1, self.spec.max_iterations + 1):
            raw = self.llm_fn(self._build_prompt(task, scratchpad))
            parsed = extract_json(raw) or {}
            thought = parsed.get("thought", "")
            tool_name = parsed.get("tool")
            observation = ""

            if tool_name and tool_name in self.tool_map:
                args = parsed.get("tool_args") or {}
                try:
                    observation = str(self.tool_map[tool_name].invoke(**args))
                except Exception as e:
                    observation = f"[TOOL ERROR] {e}"
            elif parsed.get("actions"):
                observation = json.dumps(execute_actions(parsed["actions"]))

            trace.append({"step": step, "thought": thought, "tool": tool_name, "observation": observation})
            scratchpad += f"\nStep {step}: Thought={thought} | Obs={observation}"

            if parsed.get("final_answer"):
                return {
                    "success": True,
                    "agent": self.spec.name,
                    "answer": parsed["final_answer"],
                    "steps": step,
                    "trace": trace,
                }

        return {"success": False, "agent": self.spec.name, "steps": self.spec.max_iterations, "trace": trace}
