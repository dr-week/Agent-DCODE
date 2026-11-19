"""
Pre-built Agent Archetype Templates for creating any type of domain agent in one call.
"""

from typing import Dict, List
from dcode.framework.core.spec import AgentSpec


def create_coding_agent_spec(name: str = "coder-agent") -> AgentSpec:
    return AgentSpec(
        name=name,
        role="Senior Software Engineer",
        goal="Write clean, modular, tested code inside the sandboxed workspace",
        loop_type="react",
        max_iterations=6,
    )


def create_research_agent_spec(name: str = "research-agent") -> AgentSpec:
    return AgentSpec(
        name=name,
        role="Technical Research Analyst",
        goal="Decompose complex technical questions, search code/docs, and synthesize findings",
        loop_type="reflexion",
        max_iterations=4,
    )


def create_data_analyst_spec(name: str = "data-analyst") -> AgentSpec:
    return AgentSpec(
        name=name,
        role="Data Science & Analytics Agent",
        goal="Inspect datasets, run Python statistical scripts, and produce structured insights",
        loop_type="react",
        max_iterations=5,
    )


def create_devops_sre_spec(name: str = "devops-sre") -> AgentSpec:
    return AgentSpec(
        name=name,
        role="DevOps & Site Reliability Engineer",
        goal="Monitor system processes, orchestrate services, and automate CLI-Anything harnesses",
        loop_type="react",
        max_iterations=5,
    )


def create_security_auditor_spec(name: str = "security-auditor") -> AgentSpec:
    return AgentSpec(
        name=name,
        role="Application Security Reviewer",
        goal="Audit code for vulnerabilities, path traversal, and unsafe execution patterns",
        loop_type="reflexion",
        max_iterations=3,
    )


def create_quantum_engineer_spec(name: str = "quantum-engineer") -> AgentSpec:
    return AgentSpec(
        name=name,
        role="Quantum Computing & Mechanics Engineer",
        goal="Synthesize quantum circuits (Qiskit), simulate statevectors, and solve QUBO optimization",
        loop_type="react",
        max_iterations=5,
    )


ARCHETYPE_CATALOG: Dict[str, callable] = {
    "coder": create_coding_agent_spec,
    "researcher": create_research_agent_spec,
    "data_analyst": create_data_analyst_spec,
    "devops": create_devops_sre_spec,
    "security_auditor": create_security_auditor_spec,
    "quantum": create_quantum_engineer_spec,
}


def list_archetypes() -> List[Dict[str, str]]:
    return [
        {"type": key, "name": fn().name, "role": fn().role, "loop": fn().loop_type}
        for key, fn in ARCHETYPE_CATALOG.items()
    ]
