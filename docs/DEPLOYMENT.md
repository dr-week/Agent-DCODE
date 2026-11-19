# Agent-DCODE: GitHub Deployment & Free-Tier Backend Guide

This guide details how to deploy and operate Agent-DCODE with zero infrastructure costs ($0/month) using GitHub Pages and free-tier cloud backends.

---

## 1. Frontend: Free Global CDN via GitHub Pages

The Web UI deploys automatically to GitHub Pages:
- **Live URL:** `https://<owner>.github.io/Agent-DCODE/`
- **Workflow:** `.github/workflows/deploy_pages.yml` triggers on any push affecting `src/dcode/web/static/**`.
- **Dynamic Connection:** When loaded from GitHub Pages, the UI prompts for a backend API URL (defaulting to `http://localhost:8000` for local agents, or your free cloud URL).

---

## 2. Free Cloud Backend Providers

| Provider | Specs | Setup | Limits & Mitigation |
| :--- | :--- | :--- | :--- |
| **Hugging Face Spaces** | 2 vCPU, 16GB RAM, Docker | Create Docker Space, push repo | 100% free, sleeps when idle for 48h; instant wake |
| **Render** | 512MB RAM, 0.1 CPU | Connect repo, auto-detects `render.yaml` | 750 free hrs/mo; 30s cold start after 15m idle |
| **Koyeb** | 512MB RAM, 0.1 vCPU | Connect repo via GitHub | 550 free hrs/mo; instant wake |
| **Vercel** | Serverless functions | `vercel deploy` using `src/dcode/web/serverless.py` | 100,000 requests/month; 10s execution timeout |

---

## 3. Free Databases & LLM Inference Backends

1. **Persistent Memory & Traces (Turso libSQL):**
   - 9GB storage, 1 billion row reads/month free.
   - Set `DATABASE_URL=libsql://[your-db].turso.io` and `DATABASE_AUTH_TOKEN`.
2. **Free LLM API Keys:**
   - **Google Gemini API (Google AI Studio):** Free tier provides 15 requests per minute with Gemini 2.5 Flash / 1.5 Pro.
   - **Groq Cloud:** Free tier provides 30 requests per minute with Llama 3.3 70B.
   - **Local Ollama:** Completely free offline execution via `ollama run qwen2.5-coder:7b`.

---

## 4. One-Command Local & Container Launch

```bash
# 1. Local CLI execution
python3 scripts/dcode_cli.py fix "issue description"

# 2. Local Web UI server
python3 -m dcode.web.app

# 3. Docker containerized execution
docker compose up -d
```
