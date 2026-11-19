# Agent-DCODE v2.0: Open-Source Integration Roadmap & Phased Plan

This document defines the phased engineering plan to transform **Agent-DCODE** from a generic prototype into a **production-grade Autonomous SWE & Deep-Research Platform**. Instead of writing toy implementations from scratch, each capability is powered by a battle-tested open-source GitHub project wrapped in a micro-modular adapter (`< 100 lines per file`).

---

## Target Use Case: Autonomous Issue-to-PR & Self-Healing Web Engineer

Most coding agent repos only generate snippets or edit local files. **Agent-DCODE v2.0** solves an end-to-end engineering workflow:
1. **Ingest:** Reads a GitHub Issue URL, live documentation page, or failing test log via **Crawl4AI** and **FastMCP**.
2. **Map:** Builds an AST symbol graph of the repository (`classes`, `functions`, `imports`) without blowing up the context window.
3. **Remember:** Retrieves past project conventions and bug-fix patterns from **Mem0** persistent memory.
4. **Execute & Self-Heal:** Runs a **mini-swe-agent** loop via **LiteLLM** (routing across 100+ local/cloud models), edits files, runs `pytest` or **Browser-Use** E2E UI checks, and self-corrects until green.
5. **Observe & Ship:** Exports full token/cost/latency traces via **Langfuse** and commits a clean Git branch ready for PR.

---

## Open-Source GitHub Projects to Integrate (`src/dcode/integrations/`)

All integrations live in `src/dcode/integrations/` as thin, dependency-isolated adapters under 100 lines with graceful fallback if an optional package is not installed.

| Phase | Open-Source GitHub Repo | Install Command | Adapter File (`< 100L`) | Purpose in Agent-DCODE |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 1** | [`BerriAI/litellm`](https://github.com/BerriAI/litellm) | `pip install litellm` | `src/dcode/integrations/litellm_router.py` | Unified LLM router across 100+ providers (Ollama, OpenAI, Anthropic, Gemini, Groq) with cost tracking & fallbacks |
| **Phase 1** | [`jlowin/fastmcp`](https://github.com/jlowin/fastmcp) | `pip install fastmcp` | `src/dcode/integrations/mcp_bridge.py` | Exposes DCODE tools as an MCP Server and connects to external MCP servers (GitHub, Postgres, Slack) |
| **Phase 2** | [`tree-sitter/py-tree-sitter`](https://github.com/tree-sitter/py-tree-sitter) | `pip install tree-sitter` | `src/dcode/integrations/repomap.py` | Aider-style AST RepoMap generator (Python `ast` + optional `tree-sitter` for JS/TS) |
| **Phase 2** | [`SWE-agent/mini-swe-agent`](https://github.com/SWE-agent/mini-swe-agent) | Built-in pattern | `src/dcode/framework/loops/swe_loop.py` | High-reliability Issue-to-PR loop (Reproduce -> Patch -> Test -> Git Checkpoint) |
| **Phase 3** | [`unclecode/crawl4ai`](https://github.com/unclecode/crawl4AI) | `pip install crawl4ai` | `src/dcode/integrations/crawl4ai_tool.py` | Crawls live docs, StackOverflow, and GitHub issues into clean LLM-ready Markdown |
| **Phase 3** | [`browser-use/browser-use`](https://github.com/browser-use/browser-use) | `pip install browser-use` | `src/dcode/integrations/browser_tool.py` | Headless Chromium agent that clicks UI elements, fills forms, and verifies web apps |
| **Phase 4** | [`mem0ai/mem0`](https://github.com/mem0ai/mem0) | `pip install mem0ai` | `src/dcode/integrations/mem0_store.py` | Persistent cross-session semantic memory for user preferences and repo architecture facts |
| **Phase 4** | [`langfuse/langfuse`](https://github.com/langfuse/langfuse) | `pip install langfuse` | `src/dcode/integrations/langfuse_tracer.py` | Open-source LLM observability, span tracing, token accounting, and prompt analytics |

---

## Phased Implementation Plan & Work Breakdown

### Phase 1: Universal LLM Brain & MCP Tool Bus
**Objective:** Replace single-model lock-in and custom tool glue with `LiteLLM` and `FastMCP`.

- **Deliverable 1.1 — LiteLLM Multi-Model Router (`src/dcode/integrations/litellm_router.py`):**
  - Route completions to any `provider/model` string (e.g., `ollama/qwen2.5-coder:7b`, `gemini/gemini-2.5-pro`, `anthropic/claude-3-7-sonnet`).
  - Automatic fallback chain: if a cloud API key is missing or rate-limited, fall back to local Ollama.
  - Built-in per-call token and USD cost calculation.
- **Deliverable 1.2 — FastMCP Server & Client Bridge (`src/dcode/integrations/mcp_bridge.py`):**
  - Wrap `dcode` file, edit, and `cli_anything` tools into a valid MCP server usable from Claude Desktop, Cursor, or VS Code.
  - Provide a client helper to import tools from any external MCP server into `ReActAgent` or `MultiAgentTeam`.
- **Verification Gate:** Unit test verifying multi-provider fallback and MCP tool registration in `< 100 lines` per file.

---

### Phase 2: Codebase Intelligence (RepoMap) & SWE Issue-to-PR Loop
**Objective:** Give the agent deep codebase awareness and a deterministic Git-backed bug-fixing workflow.

- **Deliverable 2.1 — AST Repository Map (`src/dcode/integrations/repomap.py`):**
  - Parse all repository files into a compact symbol tree (`file -> class -> method(args)`) ranked by reference frequency (inspired by `Aider` and `py-tree-sitter`).
- **Deliverable 2.2 — Git Checkpoint & Rollback Manager (`src/dcode/runtime/git_checkpoint.py`):**
  - Snapshot the working tree before an agent action, generate unified diffs, and auto-revert if a verification test fails.
- **Deliverable 2.3 — SWE Issue Solver Loop (`src/dcode/framework/loops/swe_loop.py`):**
  - Implement the `mini-swe-agent` 4-stage pipeline:
    1. `Locate`: Use `RepoMap` + `search_code` to pinpoint target files.
    2. `Reproduce`: Run existing test suite or write a failing reproduction script.
    3. `Patch`: Apply surgical edits via `replace_in_file`.
    4. `Verify & Commit`: Re-run tests; commit on pass or rollback and retry on failure.
- **Verification Gate:** Pass all SWE bug-fix tasks in `evals/run_evals.py`.

---

### Phase 3: Live Web Research (`Crawl4AI`) & Browser Automation (`Browser-Use`)
**Objective:** Let agents read live documentation and test real running web applications.

- **Deliverable 3.1 — Crawl4AI Web-to-Markdown Tool (`src/dcode/integrations/crawl4ai_tool.py`):**
  - Expose `@tool("crawl_url")` powered by `crawl4ai` (with stdlib HTML-to-text fallback when running offline) so agents can ingest API docs and GitHub issues.
- **Deliverable 3.2 — Browser-Use E2E UI Tester (`src/dcode/integrations/browser_tool.py`):**
  - Expose `@tool("browser_action")` wrapping `browser-use` / Playwright to open a local dev server (`http://localhost:8000`), inspect console errors, and verify UI rendering.
- **Verification Gate:** Agent crawls a documentation page, builds a web endpoint, and validates the response automatically.

---

### Phase 4: Long-Term Memory (`Mem0`) & Production Telemetry (`Langfuse`)
**Objective:** Persist knowledge across sessions and track every token, dollar, and reasoning step.

- **Deliverable 4.1 — Mem0 Persistent Memory Adapter (`src/dcode/integrations/mem0_store.py`):**
  - Wrap `mem0ai` (backed by local SQLite/Qdrant fallback) with `remember(fact, user_id)` and `recall(query, user_id)` methods plugged directly into `AgentSpec`.
- **Deliverable 4.2 — Langfuse & SQLite Observability (`src/dcode/integrations/langfuse_tracer.py`):**
  - Record every `StateGraph` node transition, LLM prompt/response, latency (ms), and token cost to Langfuse and a local SQLite trace log.
- **Verification Gate:** Query full run metrics via `/api/framework/metrics` and CLI `--json`.

---

### Phase 5: CI/CD Guardrails, Docker Sandbox & Portfolio Packaging
**Objective:** Enforce engineering discipline automatically on every push.

- **Deliverable 5.1 — GitHub Actions CI & `<100-Line` Modularity Gate (`.github/workflows/ci.yml`):**
  - Automated CI workflow running unit tests, `evals/run_evals.py`, and a strict line-count gate that fails the build if any `.py` file exceeds 100 lines.
- **Deliverable 5.2 — Containerized Execution (`Dockerfile` & `docker-compose.yml`):**
  - Isolated container runtime for safe execution of untrusted agent-generated code.
- **Deliverable 5.3 — Integration Registry Endpoint (`src/dcode/web/routes/framework_routes.py`):**
  - Expose `/api/framework/integrations` reporting live health and availability of `litellm`, `fastmcp`, `crawl4ai`, `browser-use`, `mem0`, and `langfuse`.
