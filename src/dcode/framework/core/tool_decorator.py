"""
Universal @tool decorator that introspects Python type hints & docstrings into JSON Schemas.
"""

import inspect
from typing import Any, Callable, Dict

TYPE_MAP = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
}


class ToolDefinition:
    """Wraps any Python callable with an automatically generated JSON schema."""

    def __init__(self, func: Callable[..., Any], name: str = "", description: str = ""):
        self.func = func
        self.name = name or func.__name__
        self.description = description or (inspect.getdoc(func) or f"Execute {self.name}").splitlines()[0]
        self.schema = self._build_schema(func)

    @staticmethod
    def _build_schema(func: Callable[..., Any]) -> Dict[str, Any]:
        sig = inspect.signature(func)
        properties: Dict[str, Any] = {}
        required = []
        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue
            json_type = TYPE_MAP.get(param.annotation, "string")
            properties[param_name] = {"type": json_type}
            if param.default is inspect.Parameter.empty:
                required.append(param_name)
        return {"type": "object", "properties": properties, "required": required}

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.func(*args, **kwargs)

    def invoke(self, **kwargs: Any) -> Any:
        return self.func(**kwargs)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.schema,
        }


def tool(func: Callable[..., Any] = None, *, name: str = "", description: str = "") -> Any:
    """Decorator to register any Python function as an Agentic Tool."""
    def _decorator(f: Callable[..., Any]) -> ToolDefinition:
        return ToolDefinition(f, name=name, description=description)

    return _decorator(func) if func is not None else _decorator
