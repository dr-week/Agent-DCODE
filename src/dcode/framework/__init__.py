"""
DCode Universal Agentic AI Framework SDK.
Provides declarative AgentSpec, @tool introspection, StateGraph, ReAct, Reflexion, and MultiAgentTeam.
"""

from dcode.framework.core import (
    END,
    AgentSpec,
    StateGraph,
    TaskSpec,
    ToolDefinition,
    load_agent_spec_from_dict,
    load_agent_spec_from_file,
    tool,
)
from dcode.framework.loops import ReActAgent, ReflexionAgent
from dcode.framework.swarm import MultiAgentTeam

__all__ = [
    "END",
    "AgentSpec",
    "MultiAgentTeam",
    "ReActAgent",
    "ReflexionAgent",
    "StateGraph",
    "TaskSpec",
    "ToolDefinition",
    "load_agent_spec_from_dict",
    "load_agent_spec_from_file",
    "tool",
]
