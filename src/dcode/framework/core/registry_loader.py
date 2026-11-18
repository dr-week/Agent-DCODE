"""
Declarative JSON / Dictionary loader to instantiate any AgentSpec dynamically.
"""

import json
from pathlib import Path
from typing import Any, Dict, Union
from dcode.framework.core.spec import AgentSpec


def load_agent_spec_from_dict(data: Dict[str, Any]) -> AgentSpec:
    """Construct an AgentSpec from a dictionary payload."""
    return AgentSpec(
        name=data.get("name", "custom-agent"),
        role=data.get("role", "General AI Assistant"),
        goal=data.get("goal", "Solve user tasks accurately"),
        system_prompt=data.get("system_prompt", ""),
        model=data.get("model", "qwen2.5-coder:7b"),
        loop_type=data.get("loop_type", "react"),
        max_iterations=int(data.get("max_iterations", 5)),
        tools=data.get("tools", []),
        metadata=data.get("metadata", {}),
    )


def load_agent_spec_from_file(path: Union[str, Path]) -> AgentSpec:
    """Load an AgentSpec from a JSON file on disk."""
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return load_agent_spec_from_dict(raw)
