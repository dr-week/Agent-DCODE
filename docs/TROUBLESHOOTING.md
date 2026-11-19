# Agent-DCODE: Troubleshooting & Operational Runbook

This guide diagnoses and resolves common runtime, environment, and deployment issues.

---

## 1. Environment & Package Installation

### Issue: `error: externally-managed-environment` (PEP 668 on Debian/Ubuntu)
- **Cause:** System Python prohibits global `pip install` without virtualenv.
- **Resolution:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements/base.txt
  # Or install in user space:
  pip install --user --break-system-packages flask flask-cors
  ```

---

## 2. Model & Inference Connectivity

### Issue: `URLError: Connection refused to http://localhost:11434`
- **Cause:** Local Ollama daemon is not running.
- **Resolution:**
  ```bash
  ollama serve
  ollama run qwen2.5-coder:7b
  ```
- **Fallback:** Agent-DCODE automatically falls back to stdlib offline response generators or cloud Gemini / Groq when configured.

---

## 3. Sandboxing & Runtime Execution

### Issue: `docker: command not found`
- **Behavior:** Agent-DCODE detects Docker availability dynamically via `shutil.which("docker")`.
- **Resolution:** When Docker is not installed, `DockerSandbox` falls back to isolated local subprocess execution with sanitized environment variables and execution timeouts. No manual configuration is required.

---

## 4. Web UI & GitHub Pages Connectivity

### Issue: `Network Error: Failed to fetch /api/status` on GitHub Pages
- **Cause:** Browser blocking HTTP request to `http://localhost:8000` due to Mixed Content (HTTPS page to HTTP localhost) or local backend is offline.
- **Resolution:**
  1. Open the API Endpoint bar in the Web UI header.
  2. Input your HTTPS cloud backend (e.g. Hugging Face Space URL or Render URL).
  3. Or test in Standalone Demo Mode powered by `mock_api.js`.

---

## 5. Port Conflicts

### Issue: `Address already in use: 8000`
- **Resolution:**
  ```bash
  # Check process using port 8000
  lsof -i :8000
  # Stop named services via DCODE CLI
  python3 scripts/dcode_cli.py status
  ```
