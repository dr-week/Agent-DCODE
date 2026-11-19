"""
Open-Source GitHub Integrations Package (`dcode.integrations`).
Provides modular `<100-line` adapters for LiteLLM, FastMCP, Tree-Sitter RepoMap,
Crawl4AI, Browser-Use, Mem0, Langfuse, and Quantum Mechanics (Qiskit & QUBO).
"""

from dcode.integrations.browser_tool import browser_verify, inspect_html_dom
from dcode.integrations.cli_workflows import run_fix_workflow, run_qa_workflow, run_research_workflow
from dcode.integrations.crawl4ai_tool import crawl_url, html_to_markdown
from dcode.integrations.langfuse_tracer import LangfuseTracer
from dcode.integrations.litellm_router import LiteLLMRouter
from dcode.integrations.mcp_bridge import MCPBridge
from dcode.integrations.mem0_store import Mem0Store
from dcode.integrations.quantum_engine import QuantumSimulator, quantum_optimize_qubo, simulate_quantum_circuit
from dcode.integrations.registry import get_integration_status
from dcode.integrations.repomap import RepoMap, build_repo_map

__all__ = [
    "LangfuseTracer",
    "LiteLLMRouter",
    "MCPBridge",
    "Mem0Store",
    "QuantumSimulator",
    "RepoMap",
    "browser_verify",
    "build_repo_map",
    "crawl_url",
    "get_integration_status",
    "html_to_markdown",
    "inspect_html_dom",
    "quantum_optimize_qubo",
    "run_fix_workflow",
    "run_qa_workflow",
    "run_research_workflow",
    "simulate_quantum_circuit",
]
