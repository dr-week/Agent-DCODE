# Agent-DCODE: Next-Level Engineering Roadmap & Phased Plan

This document outlines the phased roadmap to evolve **Agent-DCODE** from a modular local-first framework into a **production-grade, senior-level Agentic AI Engineering platform**. All new modules will strictly adhere to the `< 100 lines per file` micro-modular standard.

---

## Executive Summary: What Separates a Good Prototype from a Senior-Level Agent Platform

| Dimension | Current State (v1.3) | Next-Level Target (v2.0) |
| :--- | :--- | :--- |
| **LLM & Tool Protocol** | JSON-in-prompt extraction (`extract_json`) | Native Tool/Function Calling, Pydantic schema validation, and **MCP (Model Context Protocol)** client/server |
| **Execution Sandbox** | Subprocess isolated in `projects/` | Ephemeral **Docker container sandbox** with CPU/RAM/network limits and Git worktree rollback |
| **Observability** | In-memory `TransparencyTracker` + JSON logs | **OpenTelemetry (OTel) tracing**, token/cost accounting, and SQLite persistent trajectory replay |
| **Evaluation Suite** | 3 deterministic unit benchmarks (`evals/`) | **25+ SWE-bench-style coding tasks** comparing Pass@1 vs. Pass@k (self-healing) across local & cloud models |
| **Deployment & CI/CD** | Manual local scripts | GitHub Actions CI (`pytest`, `ruff`, `<100-line` linter gate), `Dockerfile`, and `docker-compose.yml` |

---

## Phase 1: Native Tool Calling & Model Context Protocol (MCP)
**Goal:** Replace fragile prompt-based JSON parsing with industry-standard structured tool execution and interoperable MCP servers.

- **1.1 Unified Provider Router (`src/dcode/llm/router.py`):**
  - Abstract `Ollama`, `OpenAI`, `Anthropic`, and `Gemini` behind one interface with automatic fallback (e.g., local Ollama for fast edits, frontier model for complex planning).
- **1.2 Strict Schema Validation (`src/dcode/framework/core/schemas.py`):**
  - Validate every LLM tool call against the `@tool` JSON Schema before execution; feed validation errors back to the agent automatically.
- **1.3 MCP Client & Server Adapter (`src/dcode/mcp/`):**
  - Expose DCode's tools (`file_tools`, `edit_tools`, `cli_anything`) as an **MCP Server** so Claude Code, Cursor, or any MCP host can use them.
  - Add an **MCP Client** so DCode agents can connect to external MCP servers (GitHub, Postgres, Playwright, Docs).

---

## Phase 2: True Containerized Sandboxing & Git Rollback
**Goal:** Make autonomous code execution safe enough for untrusted codebases and long-running self-debugging loops.

- **2.1 Docker Sandbox Runtime (`src/dcode/runtime/docker_sandbox.py`):**
  - Execute `run_python`, `run_bash`, and `run_js` inside an ephemeral Docker container with `--network=none`, memory/CPU caps, and a bind-mounted workspace.
- **2.2 Git-Backed Checkpoints (`src/dcode/runtime/git_checkpoint.py`):**
  - Automatically create lightweight Git commits/stashes before each autonomous iteration, enabling instant `diff`, `rollback`, and PR patch export.
- **2.3 AST Repository Map (`src/dcode/context/repomap.py`):**
  - Use Python `ast` (and `tree-sitter` for JS/TS) to generate a compact symbol map of classes, functions, and imports across the workspace (Aider pattern).

---

## Phase 3: Persistent Observability, Streaming & Token Economics
**Goal:** Provide production-grade debugging, cost visibility, and persistent session history.

- **3.1 SQLite Trajectory & Memory Store (`src/dcode/memory/sqlite_store.py`):**
  - Replace volatile in-memory `chat_history` and JSON flat files with a local SQLite database storing sessions, tool traces, and episodic lessons.
- **3.2 Server-Sent Events (SSE) / WebSocket Streaming (`src/dcode/web/routes/stream_routes.py`):**
  - Stream live agent thoughts, tool calls, and terminal output to the Web UI and VS Code Extension in real time instead of polling.
- **3.3 Telemetry & Cost Tracker (`src/dcode/observability/metrics.py`):**
  - Track input/output tokens, latency per node, tool error rates, and estimated API cost per task; export traces in OpenTelemetry format.

---

## Phase 4: Quantitative Agentic Benchmarks (Mini SWE-Bench)
**Goal:** Prove agent reliability with reproducible, published metrics in `README.md`.

- **4.1 Expanded Eval Dataset (`evals/tasks.json`):**
  - Expand from 3 to **25+ graded tasks** across 5 categories:
    1. Bug Fixing (multi-file Python/JS bugs with failing `pytest` suites)
    2. Feature Implementation (building modules from specs)
    3. Surgical Refactoring (renaming symbols & updating call sites)
    4. CLI-Anything Harness Generation (turning apps into `--json` CLIs)
    5. Guardrail & Security Resistance (prompt injection & path traversal tests)
- **4.2 Model Leaderboard Runner (`evals/benchmark_report.py`):**
  - Generate a markdown scorecard comparing `qwen2.5-coder:7b`, `deepseek-coder`, and `Gemini` on **Pass@1**, **Pass@k (Self-Healing)**, **Avg Iterations**, and **Latency**.

---

## Phase 5: CI/CD, Containerization & Portfolio Polish
**Goal:** Enforce architectural standards automatically and make the project one-command runnable.

- **5.1 GitHub Actions CI (`.github/workflows/ci.yml`):**
  - Run `tests/test_framework.py`, `tests/test_tools_and_cli.py`, and `evals/run_evals.py` on every push.
  - Add an automated **Modularity Gate** script that fails CI if any Python file in `src/` exceeds 100 lines.
- **5.2 Docker Compose Stack (`Dockerfile` & `docker-compose.yml`):**
  - One-command startup (`docker compose up`) for the DCode API, Web UI, and local Ollama runtime.
- **5.3 Interactive Demo Media:**
  - Record a 60-second terminal + VS Code GIF showing an autonomous agent writing code, failing a test, self-correcting, and passing all checks.
