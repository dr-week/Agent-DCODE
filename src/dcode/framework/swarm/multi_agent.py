"""
Multi-Agent Swarm & Sequential Handoff Orchestrator.
Coordinates multiple specialized agents sharing context and handing off artifacts.
"""

from typing import Any, Callable, Dict, List, Optional
from dcode.framework.core.spec import AgentSpec
from dcode.framework.loops.react_loop import ReActAgent
from dcode.framework.loops.reflexion_loop import ReflexionAgent


class MultiAgentTeam:
    """Orchestrates a team of specialized agents sequentially or via supervisor routing."""

    def __init__(
        self,
        name: str,
        members: List[AgentSpec],
        llm_fn: Optional[Callable[[str], str]] = None,
    ):
        self.name = name
        self.members = members
        self.llm_fn = llm_fn

    def _instantiate(self, spec: AgentSpec) -> Any:
        if spec.loop_type == "reflexion":
            return ReflexionAgent(spec, llm_fn=self.llm_fn)
        return ReActAgent(spec, llm_fn=self.llm_fn)

    def run(self, objective: str) -> Dict[str, Any]:
        """Run the multi-agent pipeline, passing each agent's output as context to the next."""
        shared_context = f"Team Objective: {objective}"
        handoff_log: List[Dict[str, Any]] = []

        for member_spec in self.members:
            runner = self._instantiate(member_spec)
            sub_task = f"{shared_context}\n\nYour Role ({member_spec.role}): {member_spec.goal}"
            res = runner.run(sub_task)

            output_summary = res.get("answer") or res.get("final_output") or str(res.get("trace", ""))
            handoff_log.append({
                "agent": member_spec.name,
                "role": member_spec.role,
                "success": res.get("success", False),
                "output": output_summary,
            })
            shared_context += f"\n\n[{member_spec.name} ({member_spec.role}) Output]:\n{output_summary}"

        all_ok = all(item["success"] for item in handoff_log)
        return {
            "team": self.name,
            "objective": objective,
            "success": all_ok,
            "handoffs": handoff_log,
            "final_synthesis": handoff_log[-1]["output"] if handoff_log else "",
        }
