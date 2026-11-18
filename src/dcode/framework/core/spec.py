"""
Declarative specifications for creating any Agent or Task in the DCode Framework.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class AgentSpec:
    """Declarative blueprint to instantiate any type of AI Agent."""

    name: str
    role: str
    goal: str
    system_prompt: str = ""
    model: str = "qwen2.5-coder:7b"
    loop_type: str = "react"  # react, plan_solve, reflexion
    max_iterations: int = 5
    tools: List[Any] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def build_system_instructions(self) -> str:
        base = self.system_prompt or f"You are {self.name}, acting as {self.role}."
        return f"{base}\nPrimary Goal: {self.goal}".strip()


@dataclass
class TaskSpec:
    """Specification for a unit of work assigned to an Agent or Multi-Agent Swarm."""

    description: str
    expected_output: str = "Structured JSON or verified action result"
    context: Dict[str, Any] = field(default_factory=dict)
    assigned_agent: Optional[str] = None
    validator: Optional[Callable[[Any], bool]] = None
