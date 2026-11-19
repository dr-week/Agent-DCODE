<div align="center">

<img src="docs/assets/logo.jpg" alt="Agent-DCODE Logo" width="340" style="border-radius: 14px; box-shadow: 0 10px 30px rgba(0,0,0,0.25);" />

# Agent-DCODE

### Universal Agentic AI Framework &amp; Autonomous Software Engineering Platform

*Local-First • Micro-Modular Architecture (`<100 Lines/File`) • Agent-Native CLI-Anything • Multi-Agent Swarms*

<br/>

<p align="center">
  <a href="#universal-agent-sdk--build-agents-in-10-lines"><img src="https://img.shields.io/badge/Architecture-Universal_Agent_SDK-00C853?style=for-the-badge&logo=python&logoColor=white" alt="Universal Agent SDK" /></a>
  <a href="#micro-modular-repository-map-100--100-linesfile"><img src="https://img.shields.io/badge/Modularity-100%25_%3C100_Lines%2FFile-00B0FF?style=for-the-badge&logo=codefactor&logoColor=white" alt="Modularity" /></a>
  <a href="#cli-anything-agent-native-engine"><img src="https://img.shields.io/badge/Protocol-CLI--Anything_Native-FF6D00?style=for-the-badge&logo=gnubash&logoColor=white" alt="CLI-Anything" /></a>
  <a href="#verification--benchmark-evals"><img src="https://img.shields.io/badge/Evals_Pass%401-100%25_Verified-AA00FF?style=for-the-badge&logo=checkmarx&logoColor=white" alt="Evals" /></a>
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.10+" /></a>
  <a href="https://ollama.ai/"><img src="https://img.shields.io/badge/Local_Inference-Ollama-000000?style=flat-square&logo=ollama&logoColor=white" alt="Ollama" /></a>
  <a href="https://ai.google.dev/"><img src="https://img.shields.io/badge/Cloud_Inference-Google_Gemini-4285F4?style=flat-square&logo=google&logoColor=white" alt="Gemini" /></a>
  <a href="https://flask.palletsprojects.com/"><img src="https://img.shields.io/badge/Web_Backend-Flask-000000?style=flat-square&logo=flask&logoColor=white" alt="Flask" /></a>
  <a href="vsc-agent/dcode/"><img src="https://img.shields.io/badge/IDE-VS_Code_Extension-007ACC?style=flat-square&logo=visualstudiocode&logoColor=white" alt="VS Code" /></a>
  <a href="https://www.typescriptlang.org/"><img src="https://img.shields.io/badge/TypeScript-5.0%2B-3178C6?style=flat-square&logo=typescript&logoColor=white" alt="TypeScript" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-22C55E?style=flat-square" alt="MIT License" /></a>
</p>

<p align="center">
  <a href="#executive-overview"><b>Overview</b></a> •
  <a href="#core-architectural-pillars"><b>Core Pillars</b></a> •
  <a href="#system-architecture"><b>Architecture</b></a> •
  <a href="#universal-agent-sdk--build-agents-in-10-lines"><b>Agent SDK</b></a> •
  <a href="#cli-anything-agent-native-engine"><b>CLI-Anything</b></a> •
  <a href="#micro-modular-repository-map-100--100-linesfile"><b>Repository Map</b></a> •
  <a href="#verification--benchmark-evals"><b>Benchmarks</b></a> •
  <a href="docs/README.md"><b>Documentation Hub</b></a>
</p>

</div>

---

## Executive Overview

Agent-DCODE is an open-source, air-gapped developer agent architecture and modular agentic SDK engineered from first principles. Unlike opaque SaaS wrappers or monolithic coding assistants, Agent-DCODE operates locally through models served via Ollama or remotely via Google Gemini, binding conversational intent directly to verifiable actions within a strictly sandboxed workspace.

Every Python module in the framework follows an uncompromising design constraint: **100% of codebase files are strictly under 100 lines of code**, maximizing maintainability, test isolation, and cognitive legibility.

> [!NOTE]
> **Zero Remote Data Egress:** All model tokenization, prompt evaluation, file generation, and shell executions execute within the local host boundary. No telemetry, context tokens, or code artifacts are transmitted to external cloud providers unless explicitly routed to the Gemini/Colab adapter.

---

## Core Architectural Pillars

| Architectural Pillar | Technical Scope | Engineering Highlight |
| :--- | :--- | :--- |
| **Pluggable Cognitive Loops** | ReAct, Plan-and-Solve, Reflexion (Actor / Critic), and Multi-Agent Swarms | Composable [`StateGraph`](src/dcode/framework/core/state_graph.py) directed acyclic graph and cyclical state machine |
| **Universal `@tool` &amp; ACI** | Dynamic Python function binding with automated JSON-Schema validation and surgical patching | Introspective [`@tool`](src/dcode/framework/core/tool_decorator.py) decorator and [`replace_in_file`](src/dcode/tools/edit_tools.py) |
| **CLI-Anything Engine** | Automatic generation of self-describing, agent-native CLI harnesses with `--json`, `--dry-run`, and undo stack | Modeled on research by **[HKUDS/CLI-Anything](https://github.com/HKUDS/CLI-Anything)** (*arXiv:2606.03854*) |
| **3-Tier Memory Architecture** | Working context sliding window, episodic trajectory log, and semantic BM25 RAG | Zero-dependency retrieval system in [`src/dcode/memory/`](src/dcode/memory/) |
| **Guardrails &amp; Human-in-the-Loop** | Step budget caps, path-traversal prevention, destructive command interception, and manual approval gates | [`GuardrailPolicy`](src/dcode/guardrails/policy.py) and [`ApprovalGate`](src/dcode/guardrails/approval.py) |
| **Real-Time Transparency UI** | Live streaming of execution steps, action diffs, and file tree mutations to Web and IDE surfaces | [`TransparencyTracker`](src/dcode/observability/transparency_tracker.py) backed by 7 modular Flask Blueprints |

---

## System Architecture

```mermaid
flowchart TB
    subgraph Surfaces ["Client & Surface Layer"]
        CLI["Agent-Native CLI\n(scripts/dcode_cli.py --json)"]
        Web["Flask Web UI & REST API\n(src/dcode/web/ :5000)"]
        VSC["VS Code Extension\n(vsc-agent/dcode/)"]
    end

    subgraph Framework ["Universal Agentic Framework (src/dcode/framework/)"]
        Spec["AgentSpec & TaskSpec Definitions"]
        Graph["StateGraph (Cyclical Nodes & Conditionals)"]
        Loops["Cognitive Loops: ReAct | Plan-and-Solve | Reflexion"]
        Swarm["MultiAgentTeam (Architect -> Developer -> QA)"]
    end

    subgraph Subsystems ["Core Subsystems"]
        Mem["3-Tier Memory\n(Working | Episodic | Semantic BM25)"]
        Guard["Guardrail Policies & HITL Approval Gates"]
        Obs["Observability\n(JSON Audit Store | Live Telemetry)"]
    end

    subgraph Execution ["Sandboxed Execution Layer"]
        Tools["Sandboxed ACI Tools\n(File Ops, Surgical Patching, AST Search)"]
        CLIAny["CLI-Anything Generator, Runner & Undo Stack"]
        LLM["Inference Router\n(Local Ollama | Google Gemini)"]
        Sandbox[("Sandboxed Workspace\nprojects/")]
    end

    Surfaces --> Framework
    Framework --> Subsystems
    Framework --> Execution
    Tools --> Sandbox
    CLIAny --> Sandbox
```

---

## Autonomous Execution Lifecycle

The autonomous loop executes tasks through a structured state machine with automatic heuristic error diagnostics and self-healing iterations:

```mermaid
sequenceDiagram
    autonumber
    actor Developer as Developer / IDE Surface
    participant Controller as Autonomous Controller
    participant Router as LLM Inference Router
    participant Parser as Action Parser
    participant Sandbox as Sandboxed Workspace (projects/)
    participant Tracker as Transparency Tracker

    Developer->>Controller: Dispatch High-Level Goal
    Controller->>Tracker: Emit Session Init Event

    loop Iterative Autonomous Loop (Step <= Max Iterations)
        Controller->>Router: Goal + Accumulated Context + Prior Diagnostics
        Router-->>Controller: Structured Action Schema / Plan
        Controller->>Parser: Validate JSON Block & Sanitize Directives
        alt Action Validated
            Controller->>Sandbox: Execute File Mutation / Code Subprocess
            Sandbox-->>Controller: Execution Output, Stdout & Exit Code
            Controller->>Tracker: Broadcast Step Result & File Diffs
            alt Exit Code == 0 AND Goal Complete
                Controller-->>Developer: Return Final Artifacts & Summary Report
            else Execution Diagnostic Failure
                Controller->>Controller: Ingest Error Trace into Feedback Context
            end
        else Schema Parsing Failure
            Controller->>Controller: Trigger Regex Fallback & Retry Strategy
        end
    end

    alt Iteration Limit Reached
        Controller-->>Developer: Return Checkpoint Report for Inspection
    end
```

---

## Universal Agent SDK — Build Agents in 10 Lines

Agent-DCODE provides a clean, programmatic SDK to construct domain-specific agents—from single-purpose tools to multi-agent production software teams.

### 1. Build a Custom Tool &amp; ReAct Agent (`@tool` + `AgentSpec`)

```python
from dcode.framework import AgentSpec, ReActAgent, tool

@tool
def inspect_service_latency(service: str, window_min: int = 5) -> dict:
    """Fetch p99 latency and error rate telemetry for a microservice."""
    return {"service": service, "p99_ms": 42.8, "error_rate": 0.001, "status": "healthy"}

sre_agent = ReActAgent(
    AgentSpec(
        name="sre-sentinel",
        role="Site Reliability Engineering Agent",
        goal="Diagnose service latency and recommend automated remediations",
        tools=[inspect_service_latency],
        loop_type="react",
    )
)

result = sre_agent.run("Check telemetry for payment-service and report status")
```

### 2. Multi-Agent Software Factory (`Architect -> Developer -> QA Critic`)

```python
from dcode.archetypes import create_software_team

team = create_software_team("autonomous-software-factory")
report = team.run("Design, implement, and verify a token-bucket rate limiter in projects/limiter.py")
```

### 3. Cyclical Workflows with `StateGraph`

```python
from dcode.framework import END, StateGraph

workflow = (
    StateGraph(entry_point="draft")
    .add_node("draft", lambda s: {**s, "attempt": s.get("attempt", 0) + 1, "ok": True})
    .add_node("verify", lambda s: {**s, "verified": s["ok"]})
    .add_edge("draft", "verify")
    .add_conditional_edges("verify", lambda s: END if s["verified"] else "draft")
)

final_state = workflow.run({})
```

---

## CLI-Anything Agent-Native Engine

Modeled after **[HKUDS/CLI-Anything](https://github.com/HKUDS/CLI-Anything)** (*"Making ALL Software Agent-Native"*), Agent-DCODE includes [`src/dcode/cli_anything/`](src/dcode/cli_anything/) to convert any module in `projects/` into a deterministic, agent-ready CLI interface with `--json` outputs, dry-run simulations, `SKILL.md` catalogs, and an instant **file undo/redo stack**:

```bash
# Generate an Agent-Native CLI harness + SKILL.md for any file in projects/
python3 scripts/dcode_cli.py --generate-cli projects/calculator.py --json

# List all registered CLI-Anything harnesses and discovered skills
python3 scripts/dcode_cli.py list-clis --json

# Inspect active workspace session state and trajectory log
python3 scripts/dcode_cli.py status --json

# Roll back the most recent file mutation from the snapshot stack
python3 scripts/dcode_cli.py undo --json
```

---

## Micro-Modular Repository Map (`100% < 100 Lines/File`)

Every Python module in `src/dcode/` is strictly bounded below 100 lines of code (maximum size: **97 lines**):

```text
Agent-DCODE/
├── README.md                              # Main architectural overview & guide
├── pyproject.toml                         # Packaging and CLI console entrypoints
├── requirements/                          # Categorized dependency manifests
│   ├── base.txt                           # Core runtime requirements
│   ├── colab.txt                          # Cloud notebook & tunnel dependencies
│   └── dev.txt                            # Linting and testing dependencies
├── docs/                                  # 49 technical guides across 8 categories
│   └── assets/logo.jpg                    # Official project banner visual
│
├── src/dcode/                             # CORE FRAMEWORK & ENGINE (<100 lines/file)
│   ├── config.py                          # Environment paths, port assignments & LLM configs
│   ├── framework/                         # 1. Universal Agent Creation SDK
│   │   ├── core/                          # AgentSpec, @tool decorator, StateGraph, JSON loader
│   │   ├── loops/                         # ReActAgent & ReflexionAgent (Actor / Critic)
│   │   └── swarm/                         # MultiAgentTeam sequential and supervisor handoffs
│   ├── memory/                            # 2. 3-Tier Memory (Working, Episodic, Semantic BM25)
│   ├── guardrails/                        # 3. Policy engines & Human-in-the-Loop gates
│   ├── archetypes/                        # 4. Pre-built templates (Coder, Researcher, DevOps, QA)
│   ├── cli_anything/                      # 5. HKUDS/CLI-Anything harness generator, runner & undo
│   ├── agents/                            # 6. Autonomous & Codex coding loops
│   ├── tools/                             # 7. Sandboxed ACI tools (file, patch, AST, subprocess)
│   ├── llm/                               # 8. Ollama and Gemini clients with resilient JSON parser
│   ├── context/                           # 9. Workspace context extractors and prompt builder
│   ├── observability/                     # 10. Structured JSON audit logger and live tracker
│   ├── orchestrator/                      # 11. Process lifecycle management and health monitoring
│   └── web/                               # 12. Modular Flask application with 7 route blueprints
│
├── scripts/                               # CLI entrypoints (dcode_cli.py, dcode_orchestrator.py, run_web.py)
├── tests/                                 # Zero-dependency unit test suite
├── evals/                                 # Automated agent benchmark suite (tasks.json, run_evals.py)
├── releases/                              # Packaged VS Code extension bundle (agent-dcode-0.1.0.vsix)
├── vsc-agent/                             # Native TypeScript VS Code Extension source
└── projects/                              # Sandboxed AI Workspace Boundary
```

---

## Verification &amp; Benchmark Evals

Agent-DCODE includes an automated verification benchmark suite in `evals/` assessing code generation, surgical refactoring, and agent-native CLI generation:

```bash
# Execute Framework Unit Tests (StateGraph, @tool, ReAct, Reflexion, Swarm, Memory, Guardrails)
python3 tests/test_framework.py -v

# Execute Sandboxed Tool & CLI-Anything Tests
python3 tests/test_tools_and_cli.py -v

# Execute Automated End-to-End Evaluation Benchmark Suite
python3 evals/run_evals.py
```

### Evaluation Benchmark Results

| Benchmark Suite | Focus / Subsystem | Assertions | Pass Rate | Mean Latency | Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Universal Framework Suite** | `@tool`, `StateGraph`, `ReAct`, `Reflexion`, `Swarm`, Memory, Guardrails | 5 Test Cases | **100% (5/5)** | `< 5 ms` | Verified |
| **Sandboxed Tools &amp; CLI** | Resilient JSON parsing, `safe_path`, `replace_in_file`, CLI harness &amp; undo | 4 Test Cases | **100% (4/4)** | `~30 ms` | Verified |
| **End-to-End Evals** | Code synthesis, surgical editing, and self-describing CLI generation | 3 Benchmarks | **100% (3/3)** | `~60 ms` | Verified |

---

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/dr-week/Agent-DCODE.git
cd Agent-DCODE

# Create and activate an isolated virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1

# Install core runtime dependencies
pip install -r requirements/base.txt
```

### 2. Configure Inference Model

```bash
# Start the Ollama local daemon
ollama serve

# Pull the recommended code generation model
ollama pull qwen2.5-coder:7b
```

### 3. Launch Services

```bash
# Option A: Start both Ollama and the Flask Web Dashboard via the Service Orchestrator
python3 scripts/dcode_orchestrator.py start

# Option B: Launch the Flask Web Dashboard directly on http://localhost:5000
python3 scripts/run_web.py

# Option C: Execute an autonomous coding goal directly via CLI
python3 scripts/dcode_cli.py --goal "Build a rate limiter in projects/limiter.py" --json
```

---

## VS Code Extension Integration

The VS Code extension bridges your editor directly to the local Agent-DCODE engine:

- **Integrated Chat Sidebar:** Real-time conversational interface connected to workspace files.
- **Model Switching:** Instant toggling between local Ollama models and remote endpoints.
- **Process Manager:** Automatic lifecycle management, process monitoring, and health checking for Ollama.
- **Transparency Panel:** Live visual inspection of executed actions, modified files, and diff previews.

Install the packaged bundle directly:
```bash
code --install-extension releases/agent-dcode-0.1.0.vsix
```

---

## Security &amp; Sandboxing Model

Agent-DCODE enforces defense-in-depth safety boundaries to protect host systems during autonomous runs:

- **Strict Path Sandboxing:** File operations (`write_file`, `replace_in_file`, `create_file`) are bounded within `projects/`. Traversal patterns such as `../` trigger immediate termination.
- **Process Execution Caps:** All subprocess calls invoked through the executor enforce a hard 30-second timeout to prevent runaway executions.
- **High-Risk Gate Interception:** High-risk actions require explicit human approval via the [`ApprovalGate`](src/dcode/guardrails/approval.py) before execution.

> [!IMPORTANT]
> The agent executes scripts and code within the `projects/` directory using host runtime privileges. Always execute Agent-DCODE under an unprivileged user account and avoid running with root or administrative credentials.

---

## Documentation Hub (49 Technical Specifications)

Full architectural specifications, developer manuals, and operational references are cataloged in **[docs/README.md](docs/README.md)**:

| Documentation Section | Directory | Scope |
| :--- | :--- | :--- |
| **01. Getting Started** | [`docs/01-getting-started/`](docs/01-getting-started/) | Onboarding tutorials, 50+ practical prompt examples, and Colab guides |
| **02. Autonomous Engine** | [`docs/02-autonomous-engine/`](docs/02-autonomous-engine/) | Deep dive into autonomous loops, state recovery, and loop integrations |
| **03. Agents &amp; Tools** | [`docs/03-agents-and-tools/`](docs/03-agents-and-tools/) | Codex agent specification, control bar protocols, and logging guides |
| **04. Transparency &amp; UI** | [`docs/04-transparency-and-ui/`](docs/04-transparency-and-ui/) | Real-time telemetry streaming architecture and file panel reference |
| **05. Orchestrator &amp; Ops** | [`docs/05-orchestrator-and-ops/`](docs/05-orchestrator-and-ops/) | Multi-process orchestrator, health monitors, and operational runbooks |
| **06. VS Code Extension** | [`docs/06-vscode-extension/`](docs/06-vscode-extension/) | Extension architecture, process manager specs, and debugging manuals |
| **07. Testing &amp; Verification** | [`docs/07-testing-and-verification/`](docs/07-testing-and-verification/) | Verification checklists, testing matrices, and web UI test scenarios |
| **08. Releases &amp; Reports** | [`docs/08-releases-and-reports/`](docs/08-releases-and-reports/) | Full version release notes (`v0.1.0` through `v1.3.0`) and changelogs |

---

## Development Roadmap

- [x] Pluggable Cognitive Loop Architecture (`ReAct`, `Reflexion`, `Plan-and-Solve`)
- [x] Universal `@tool` decorator with JSON-Schema validation
- [x] Multi-Agent Swarm coordination (`Architect -> Developer -> QA Critic`)
- [x] HKUDS/CLI-Anything native integration with automatic file undo stack
- [x] Micro-modular refactor maintaining `< 100 lines of code` across all Python files
- [x] Real-time transparency streaming and file panel telemetry
- [x] Zero-dependency test and benchmark evaluation suite (`evals/`)
- [ ] SQLite-backed persistent conversation state and session checkpoints
- [ ] Automated Git branch and commit generation per autonomous goal
- [ ] Rootless Docker container distribution for isolated sandboxing

---

## License

This project is open-source and released under the [MIT License](LICENSE).

<div align="center">
  <sub>Agent-DCODE • Engineering Autonomous Software Systems Locally</sub>
</div>
