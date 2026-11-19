"""
Phase 5: Open-Source Integration Registry & Health Inspector.
Reports availability, active backend (upstream library vs. zero-dependency stdlib fallback),
and GitHub source repository for every integrated project.
"""

from typing import Any, Dict, List
from dcode.integrations.browser_tool import HAS_BROWSER_USE
from dcode.integrations.crawl4ai_tool import HAS_CRAWL4AI
from dcode.integrations.langfuse_tracer import HAS_LANGFUSE
from dcode.integrations.litellm_router import HAS_LITELLM
from dcode.integrations.mcp_bridge import HAS_FASTMCP
from dcode.integrations.mem0_store import HAS_MEM0
from dcode.integrations.repomap import HAS_TREESITTER


def get_integration_status() -> List[Dict[str, Any]]:
    """Return status catalog of all open-source GitHub project integrations."""
    return [
        {
            "id": "litellm",
            "phase": 1,
            "github_repo": "https://github.com/BerriAI/litellm",
            "installed": HAS_LITELLM,
            "active_backend": "litellm" if HAS_LITELLM else "ollama-stdlib-router",
            "adapter": "dcode.integrations.litellm_router.LiteLLMRouter",
        },
        {
            "id": "fastmcp",
            "phase": 1,
            "github_repo": "https://github.com/jlowin/fastmcp",
            "installed": HAS_FASTMCP,
            "active_backend": "fastmcp-v3" if HAS_FASTMCP else "jsonrpc-mcp-bridge",
            "adapter": "dcode.integrations.mcp_bridge.MCPBridge",
        },
        {
            "id": "tree-sitter",
            "phase": 2,
            "github_repo": "https://github.com/tree-sitter/py-tree-sitter",
            "installed": HAS_TREESITTER,
            "active_backend": "tree-sitter+ast" if HAS_TREESITTER else "python-ast-repomap",
            "adapter": "dcode.integrations.repomap.RepoMap",
        },
        {
            "id": "mini-swe-agent",
            "phase": 2,
            "github_repo": "https://github.com/SWE-agent/mini-swe-agent",
            "installed": True,
            "active_backend": "dcode-swe-loop",
            "adapter": "dcode.framework.loops.swe_loop.SWELoop",
        },
        {
            "id": "crawl4ai",
            "phase": 3,
            "github_repo": "https://github.com/unclecode/crawl4AI",
            "installed": HAS_CRAWL4AI,
            "active_backend": "crawl4ai-async" if HAS_CRAWL4AI else "stdlib-html2md",
            "adapter": "dcode.integrations.crawl4ai_tool.crawl_url",
        },
        {
            "id": "browser-use",
            "phase": 3,
            "github_repo": "https://github.com/browser-use/browser-use",
            "installed": HAS_BROWSER_USE,
            "active_backend": "browser-use" if HAS_BROWSER_USE else "stdlib-dom-inspector",
            "adapter": "dcode.integrations.browser_tool.browser_verify",
        },
        {
            "id": "mem0",
            "phase": 4,
            "github_repo": "https://github.com/mem0ai/mem0",
            "installed": HAS_MEM0,
            "active_backend": "mem0ai" if HAS_MEM0 else "sqlite-semantic-store",
            "adapter": "dcode.integrations.mem0_store.Mem0Store",
        },
        {
            "id": "langfuse",
            "phase": 4,
            "github_repo": "https://github.com/langfuse/langfuse",
            "installed": HAS_LANGFUSE,
            "active_backend": "langfuse-cloud" if HAS_LANGFUSE else "sqlite-otel-spans",
            "adapter": "dcode.integrations.langfuse_tracer.LangfuseTracer",
        },
    ]
