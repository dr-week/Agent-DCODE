"""
Phase 1: FastMCP Server & Client Bridge Adapter (jlowin/fastmcp).
Exposes Agent-DCODE tools as an MCP-compliant server and imports external MCP tools
into AgentSpec tool registries.
"""

from typing import Any, Callable, Dict, List, Optional
from dcode.framework.core.tool_decorator import ToolDefinition, tool
from dcode.tools.edit_tools import replace_in_file, search_code
from dcode.tools.file_tools import list_files, read_file, write_file

try:
    from fastmcp import FastMCP  # type: ignore

    HAS_FASTMCP = True
except ImportError:
    FastMCP = None  # type: ignore
    HAS_FASTMCP = False


class MCPBridge:
    """Universal Model Context Protocol (MCP) adapter powered by FastMCP with stdlib JSON-RPC fallback."""

    def __init__(self, server_name: str = "Agent-DCODE-MCP"):
        self.server_name = server_name
        self.tools: Dict[str, ToolDefinition] = {}
        self.mcp_app = FastMCP(server_name) if HAS_FASTMCP and FastMCP else None
        self._register_defaults()

    def _register_defaults(self) -> None:
        """Register core Agent-DCODE file and surgical code tools into the MCP bus."""
        self.register_function("read_file", "Read a workspace file", read_file)
        self.register_function("write_file", "Write a workspace file", write_file)
        self.register_function("list_files", "List all workspace files", list_files)
        self.register_function("replace_in_file", "Surgical string replacement in file", replace_in_file)
        self.register_function("search_code", "Search regex pattern across repository", search_code)

    def register_function(self, name: str, description: str, fn: Any) -> ToolDefinition:
        """Register any callable or ToolDefinition as both an MCP tool and a DCode ToolDefinition."""
        tdef = fn if isinstance(fn, ToolDefinition) else tool(name=name, description=description)(fn)
        self.tools[name] = tdef
        if self.mcp_app is not None:
            raw_fn = tdef.func if isinstance(fn, ToolDefinition) else fn
            self.mcp_app.tool(name=name, description=description)(raw_fn)
        return tdef

    def list_mcp_tools(self) -> List[Dict[str, Any]]:
        """Return MCP-standard tools/list JSON schema."""
        return [
            {
                "name": t.name,
                "description": t.description,
                "inputSchema": t.schema,
            }
            for t in self.tools.values()
        ]

    def call_mcp_tool(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute an MCP tools/call request and return standard MCP content blocks."""
        if name not in self.tools:
            return {"isError": True, "content": [{"type": "text", "text": f"Unknown MCP tool: {name}"}]}
        try:
            res = self.tools[name].invoke(**(arguments or {}))
            return {"isError": False, "content": [{"type": "text", "text": str(res)}], "raw": res}
        except Exception as exc:
            return {"isError": True, "content": [{"type": "text", "text": str(exc)}]}
