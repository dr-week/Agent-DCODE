# 🤖 Agent-DCODE — Universal Agentic AI Framework & Coding Agent

**Agent-DCODE** is a local-first **Universal Agentic AI Framework & Autonomous Software Engineering Platform**. Built from first principles in strictly modular `<100-line` Python files, it lets you create **any type of single-agent or multi-agent system** (Coder, Researcher, Data Analyst, DevOps SRE, Security Auditor, or Multi-Agent Software Factory) using local LLMs (Ollama) or frontier APIs (Gemini/Colab), with native **[CLI-Anything](https://github.com/HKUDS/CLI-Anything)** (`arXiv:2606.03854`) support, a Flask Web UI, and a VS Code Extension.

![Status](https://img.shields.io/badge/Status-Production_v1.3-green)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Architecture](https://img.shields.io/badge/Modularity-100%25_%3C100_Lines_Per_File-brightgreen)
![CLI-Anything](https://img.shields.io/badge/Agent--Native-CLI--Anything-orange)
![Evals](https://img.shields.io/badge/Evals_Pass%401-100%25-brightgreen)

---

## 🏗️ Modular Folder & Subfolder Architecture

Every code module in `src/dcode/`, `scripts/`, `tests/`, and `evals/` is strictly **under 100 lines** and organized by functional domain:

```text
Agent-DCODE/
├── README.md                              # Portfolio overview, quickstart & SDK examples
├── pyproject.toml                         # Package config & CLI entrypoints (dcode, dcode-orch, dcode-web)
├── requirements/                          # Dependency manifests (base.txt, colab.txt, dev.txt)
├── docs/                                  # 47+ docs organized in 8 functional subfolders (see docs/README.md)
│
├── src/dcode/                             # CORE AGENTIC AI FRAMEWORK & ENGINE (<100 lines/file)
│   ├── config.py                          # Centralized workspace paths, ports & LLM configuration
│   │
│   ├── framework/                         # 1. UNIVERSAL AGENT CREATION SDK
│   │   ├── core/                          # Declarative primitives & graph state machine
│   │   │   ├── spec.py                    # AgentSpec & TaskSpec blueprints
│   │   │   ├── tool_decorator.py          # @tool decorator (auto JSON-schema from Python type hints)
│   │   │   ├── state_graph.py             # LangGraph-style DAG & cyclical StateGraph runner
│   │   │   └── registry_loader.py         # Instantiate any agent dynamically from JSON/dict
│   │   ├── loops/                         # Pluggable cognitive reasoning loops
│   │   │   ├── react_loop.py              # ReAct loop (Thought → Tool Call → Observation → Answer)
│   │   │   └── reflexion_loop.py          # Actor ↔ Critic self-refinement loop
│   │   └── swarm/                         # Multi-agent orchestration
│   │       └── multi_agent.py             # MultiAgentTeam sequential & supervisor handoffs
│   │
│   ├── memory/                            # 2. 3-TIER AGENT MEMORY SYSTEM
│   │   ├── working.py                     # Sliding-window message buffer & key-value scratchpad
│   │   ├── episodic.py                    # Persistent trajectory & error-recovery lesson store
│   │   └── semantic_rag.py                # Zero-dependency BM25 semantic retrieval over docs/code
│   │
│   ├── guardrails/                        # 3. SAFETY POLICIES & HUMAN-IN-THE-LOOP (HITL)
│   │   ├── policy.py                      # Step budgets, shell restrictions & path-traversal blocks
│   │   └── approval.py                    # HITL approval gates for high-risk actions
│   │
│   ├── archetypes/                        # 4. PRE-BUILT AGENT TEMPLATES ("Create Any Agent")
│   │   ├── templates.py                   # Coder, Researcher, DataAnalyst, DevOps SRE, SecurityAuditor
│   │   └── software_team.py               # 3-Agent Software Factory (Architect → Developer → QA Critic)
│   │
│   ├── cli_anything/                      # 5. HKUDS/CLI-ANYTHING HARNESS INTEGRATION
│   │   ├── generator.py                   # AST analyzer & 7-phase agent-native CLI generator
│   │   ├── runner.py                      # Deterministic --json & --dry-run CLI harness runner
│   │   ├── session.py                     # Stateful session.json trajectory & file Undo/Redo stack
│   │   └── skill_doc.py                   # Auto-generates SKILL.md manifests for agent discovery
│   │
│   ├── agents/                            # 6. AUTONOMOUS & CODEX CODING AGENTS
│   │   ├── autonomous.py                  # Continuous Plan → Act → Verify → Iterate coding loop
│   │   ├── codex.py                       # Single-cycle Codex coding agent
│   │   ├── planner.py                     # Structured LLM plan & action generator
│   │   ├── verifier.py                    # Exit-code, syntax & goal completion verifier
│   │   └── prompts.py                     # Prompt templates for planning & tool execution
│   │
│   ├── tools/                             # 7. SANDBOXED EXECUTION TOOLS
│   │   ├── file_tools.py                  # safe_path, write_file, append_file, read_file, list_files
│   │   ├── edit_tools.py                  # Surgical replace_in_file & regex search_code
│   │   ├── code_tools.py                  # Subprocess-isolated run_python, run_bash, run_js
│   │   ├── system_tools.py                # get_processes & show_progress
│   │   └── executor.py                    # Central action dispatcher with --dry-run support
│   │
│   ├── llm/                               # 8. MODEL CLIENTS & ROBUST PARSER
│   │   ├── ollama_client.py               # Local Ollama client (zero-dependency urllib support)
│   │   ├── gemini_client.py               # Google Gemini API client & memory checks
│   │   ├── colab_server.py                # Remote Colab + ngrok server
│   │   └── parser.py                      # Fence-aware JSON extractor & schema validator
│   │
│   ├── context/                           # 9. WORKSPACE CONTEXT MANAGEMENT
│   │   ├── extractors.py                  # File, directory tree & code snippet extractors
│   │   └── builder.py                     # Token-budgeted (<2KB) prompt context builder
│   │
│   ├── observability/                     # 10. LOGGING & REAL-TIME TRANSPARENCY
│   │   ├── log_store.py                   # Per-project JSON log storage & auto-pruning
│   │   ├── log_formatter.py               # State recovery & human-readable log summaries
│   │   ├── transparency_tracker.py        # Real-time UI step, action & progress state tracker
│   │   └── transparency_session.py        # Thread-safe session singleton manager
│   │
│   ├── orchestrator/                      # 11. SERVICE LIFECYCLE ORCHESTRATOR
│   │   ├── models.py                      # Service & ServiceStatus models
│   │   ├── health.py                      # TCP port & HTTP /health checks
│   │   ├── processes.py                   # Process discovery & duplicate cleanup
│   │   ├── lifecycle.py                   # Start/stop handlers for Backend & Ollama
│   │   └── manager.py                     # High-level Orchestrator facade
│   │
│   └── web/                               # 12. FLASK WEB SERVER & BLUEPRINTS
│       ├── app.py                         # Flask application factory
│       ├── state.py                       # Shared server state
│       ├── routes/                        # 7 Modular Route Blueprints (chat, agent, framework, cli_anything, files, logs, transparency)
│       └── static/                        # Frontend Web UI (index.html, script.js, style.css)
│
├── scripts/                               # CLI ENTRYPOINTS (dcode_cli.py, dcode_orchestrator.py, run_web.py)
├── tests/                                 # UNIT & FRAMEWORK TESTS (test_framework.py, test_tools_and_cli.py)
├── evals/                                 # AUTOMATED BENCHMARK SUITE (run_evals.py, tasks.json)
├── releases/                              # Packaged VSIX binaries
├── vsc-agent/                             # VS Code Extension
└── projects/                              # Sandboxed AI Workspace
```

---

## ⚡ Create Any Type of Agent in 10 Lines of Python

### 1. Custom Tool + ReAct Agent (`@tool` + `AgentSpec`)
```python
from dcode.framework import AgentSpec, ReActAgent, tool

@tool
def query_service_latency(service: str, percentile: int = 99) -> dict:
    """Return latency metrics in milliseconds for a target service."""
    return {"service": service, "p99_ms": 48.2, "status": "healthy"}

spec = AgentSpec(
    name="sre-diagnostic-agent",
    role="Site Reliability Engineer",
    goal="Diagnose service health using telemetry tools",
    tools=[query_service_latency],
)
agent = ReActAgent(spec)
```

### 2. Multi-Agent Software Factory (`Architect → Developer → QA Critic`)
```python
from dcode.archetypes import create_software_team

team = create_software_team()
result = team.run("Design, implement, and verify a token-bucket rate limiter")
```

### 3. Custom Workflow Graph (`StateGraph`)
```python
from dcode.framework import END, StateGraph

graph = StateGraph(entry_point="retrieve")
graph.add_node("retrieve", lambda s: {**s, "docs": ["doc1"]})
graph.add_node("synthesize", lambda s: {**s, "summary": f"Synthesized {len(s['docs'])} docs"})
graph.add_edge("retrieve", "synthesize")
graph.add_edge("synthesize", END)
state = graph.run({})
```

---

## 🧪 Verification & Benchmark Evals

Run the unit tests and the automated benchmark evaluation suite:

```bash
# 1. Universal Agentic Framework Tests (5/5 passing)
python3 tests/test_framework.py -v

# 2. Sandboxed Tools & CLI-Anything Harness Tests (4/4 passing)
python3 tests/test_tools_and_cli.py -v

# 3. Automated Evals Benchmark Suite (100% Pass@1)
python3 evals/run_evals.py
```

---

## 📚 Documentation Hub

Browse **[docs/README.md](docs/README.md)** for the full 8-folder documentation hierarchy.
