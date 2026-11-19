"""
Phase 5: Open-Source Integration Registry & Health Inspector.
Reports availability, active backend, and GitHub source repository for every integrated project.
"""

from typing import Any, Dict, List
from dcode.integrations.browser_tool import HAS_BROWSER_USE
from dcode.integrations.crawl4ai_tool import HAS_CRAWL4AI
from dcode.integrations.langfuse_tracer import HAS_LANGFUSE
from dcode.integrations.litellm_router import HAS_LITELLM
from dcode.integrations.mcp_bridge import HAS_FASTMCP
from dcode.integrations.mem0_store import HAS_MEM0
from dcode.integrations.quantum_engine import HAS_QISKIT
from dcode.integrations.repomap import HAS_TREESITTER


def get_integration_status() -> List[Dict[str, Any]]:
    """Return status catalog of all 9 open-source GitHub project integrations."""
    return [
        {"id": "litellm", "github_repo": "https://github.com/BerriAI/litellm", "installed": HAS_LITELLM, "backend": "litellm" if HAS_LITELLM else "ollama-stdlib"},
        {"id": "fastmcp", "github_repo": "https://github.com/jlowin/fastmcp", "installed": HAS_FASTMCP, "backend": "fastmcp" if HAS_FASTMCP else "jsonrpc-bridge"},
        {"id": "tree-sitter", "github_repo": "https://github.com/tree-sitter/py-tree-sitter", "installed": HAS_TREESITTER, "backend": "tree-sitter" if HAS_TREESITTER else "python-ast"},
        {"id": "mini-swe-agent", "github_repo": "https://github.com/SWE-agent/mini-swe-agent", "installed": True, "backend": "dcode-swe-loop"},
        {"id": "crawl4ai", "github_repo": "https://github.com/unclecode/crawl4AI", "installed": HAS_CRAWL4AI, "backend": "crawl4ai" if HAS_CRAWL4AI else "stdlib-html2md"},
        {"id": "browser-use", "github_repo": "https://github.com/browser-use/browser-use", "installed": HAS_BROWSER_USE, "backend": "browser-use" if HAS_BROWSER_USE else "stdlib-dom"},
        {"id": "mem0", "github_repo": "https://github.com/mem0ai/mem0", "installed": HAS_MEM0, "backend": "mem0ai" if HAS_MEM0 else "sqlite-store"},
        {"id": "langfuse", "github_repo": "https://github.com/langfuse/langfuse", "installed": HAS_LANGFUSE, "backend": "langfuse" if HAS_LANGFUSE else "sqlite-otel"},
        {"id": "qiskit", "github_repo": "https://github.com/Qiskit/qiskit", "installed": HAS_QISKIT, "backend": "qiskit-aer" if HAS_QISKIT else "stdlib-quantum-sim"},
    ]
