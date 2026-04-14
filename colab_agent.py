import json
import logging
import os
import re
import time

import psutil
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from pyngrok import ngrok
from logger import write_log, get_last_state

MAX_CODE_LENGTH = 2000
MEMORY_THRESHOLD_BYTES = 600 * 1024 * 1024  # 600 MB free required
MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
API_KEY = os.getenv("GOOGLE_API_KEY")
TIMEOUT_SECONDS = 20

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("colab_agent")

app = Flask(__name__)
CORS(app)


class ColabAgentError(Exception):
    pass


def check_environment() -> None:
    if not API_KEY:
        raise ColabAgentError(
            "GOOGLE_API_KEY not set. In Colab set os.environ['GOOGLE_API_KEY'] = '<YOUR_KEY>'"
        )


def check_memory() -> None:
    memory = psutil.virtual_memory()
    logger.debug("Memory available: %s MB", memory.available // 1024 // 1024)
    if memory.available < MEMORY_THRESHOLD_BYTES:
        raise ColabAgentError(
            "Colab RAM is low. Free memory below 600MB. Close other notebooks or restart the runtime."
        )


def extract_json(text: str) -> dict:
    text = text.strip()
    logger.debug("Raw model output: %s", text[:800])

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to extract the first JSON object from the output.
        match = re.search(r"\{.*\}", text, re.S)
        if not match:
            raise
        return json.loads(match.group(0))


def build_prompt(task: str, code: str) -> str:
    code_snippet = f"\n\nCode:\n{code}" if code else ""
    return f"""
You are a concise expert coding assistant.

Task: {task}
{code_snippet}

Constraints:
- Use a single API call.
- Return ONLY valid JSON.
- Keep code responses concise and safe for Colab.
- If code is provided, use it as context and do not exceed 2000 characters.
- Do not include any explanation outside the JSON object.

Output format:
{{
  "plan": ["step 1", "step 2"],
  "actions": [
    {{"type": "write_file", "path": "projects/main.py", "content": "print(\"hello\")"}},
    {{"type": "run_python", "code": "print(\"run\")"}}
  ],
  "result": "Summary of the result or next step."
}}
""".strip()


def call_gemini(prompt: str) -> str:
    check_environment()
    url = f"https://generativelanguage.googleapis.com/v1beta2/models/{MODEL}:generate"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "prompt": {"text": prompt},
        "temperature": 0.2,
        "max_output_tokens": 800,
    }

    logger.info("Calling Gemini model %s", MODEL)
    response = requests.post(url, headers=headers, json=body, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    payload = response.json()

    if "candidates" not in payload or not payload["candidates"]:
        raise ColabAgentError("Gemini response did not include candidates.")

    candidate = payload["candidates"][0]
    content = candidate.get("content", [])
    if isinstance(content, list):
        text = "".join([item.get("text", "") for item in content if item.get("type") == "output_text" or item.get("type") == "text"])
    else:
        text = candidate.get("output", "") or candidate.get("text", "")

    if not text:
        raise ColabAgentError("Gemini returned empty text content.")

    return text


@app.route("/agent", methods=["POST"])
def agent_endpoint():
    start_time = time.time()

    try:
        check_memory()
        payload = request.get_json(force=True)
        task = (payload.get("task") or "").strip()
        code = payload.get("code", "") or ""

        if not task:
            return jsonify({"error": "Task field is required."}), 400

        if len(code) > MAX_CODE_LENGTH:
            return jsonify({
                "error": f"Code payload too long: maximum {MAX_CODE_LENGTH} characters.",
                "length": len(code),
            }), 400

        prompt = build_prompt(task, code)
        raw = call_gemini(prompt)
        result = extract_json(raw)

        plan = result.get("plan", [])
        actions = result.get("actions", [])
        summary = result.get("result", "")

        # Log to colab_agent project
        write_log("colab_agent", task, f"gemini({MODEL})", "success", summary)

        return jsonify({
            "success": True,
            "task": task,
            "model": MODEL,
            "plan": plan,
            "actions": actions,
            "result": summary,
            "raw": raw,
            "runtime_seconds": round(time.time() - start_time, 2),
        })

    except ColabAgentError as exc:
        logger.error("Agent error: %s", exc)
        write_log("colab_agent", task, "error", "fail", str(exc))
        return jsonify({"success": False, "error": str(exc)}), 500
    except requests.exceptions.RequestException as exc:
        logger.exception("API request failed")
        write_log("colab_agent", task, "api_error", "fail", str(exc))
        return jsonify({"success": False, "error": "Gemini request failed", "detail": str(exc)}), 502
    except json.JSONDecodeError as exc:
        logger.exception("JSON parse failed")
        write_log("colab_agent", task, "parse_error", "fail", str(exc))
        return jsonify({"success": False, "error": "Failed to parse model JSON output", "detail": str(exc)}), 500
    except Exception as exc:
        logger.exception("Unexpected error")
        write_log("colab_agent", task, "unknown_error", "fail", str(exc))
        return jsonify({"success": False, "error": str(exc)}), 500


@app.route("/health", methods=["GET"])
def health_endpoint():
    memory = psutil.virtual_memory()
    return jsonify({
        "status": "healthy",
        "model": MODEL,
        "port": 5000,
        "free_memory_mb": memory.available // 1024 // 1024,
        "total_memory_mb": memory.total // 1024 // 1024,
    })


def start_tunnel(port: int = 5000) -> str:
    public_url = ngrok.connect(port, bind_tls=True).public_url
    logger.info("ngrok tunnel started at %s", public_url)
    return public_url


def start_colab_server(port: int = 5000, use_ngrok: bool = True):
    if use_ngrok:
        public_url = start_tunnel(port)
        print(f"Public URL: {public_url}")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    print("Starting minimal Colab Codex agent...")
    start_colab_server()
