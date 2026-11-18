"""
Multi-Agent Software Engineering Team (Architect → Developer → QA Critic).
"""

from typing import Callable, Optional
from dcode.framework.core.spec import AgentSpec
from dcode.framework.swarm.multi_agent import MultiAgentTeam


def create_software_team(
    team_name: str = "autonomous-software-factory",
    llm_fn: Optional[Callable[[str], str]] = None,
) -> MultiAgentTeam:
    """Create a 3-agent software team: System Architect → Code Builder → QA Critic."""
    architect = AgentSpec(
        name="architect",
        role="Lead Software Architect",
        goal="Design a clean, modular <100-line-per-file architecture and interface plan",
        loop_type="react",
        max_iterations=3,
    )
    developer = AgentSpec(
        name="developer",
        role="Principal Python Developer",
        goal="Implement the architect's design using sandboxed file and code execution tools",
        loop_type="react",
        max_iterations=5,
    )
    qa_critic = AgentSpec(
        name="qa-critic",
        role="QA & Verification Engineer",
        goal="Verify implementation correctness, edge cases, and test coverage",
        loop_type="reflexion",
        max_iterations=3,
    )
    return MultiAgentTeam(
        name=team_name,
        members=[architect, developer, qa_critic],
        llm_fn=llm_fn,
    )
