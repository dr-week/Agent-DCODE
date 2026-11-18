"""
Colab remote Flask server with optional ngrok tunnel for Gemini execution.
"""

import time
import psutil
from flask import Flask, jsonify, request
from flask_cors import CORS
from dcode.config import GEMINI_MODEL
from dcode.llm.gemini_client import (
    ColabAgentError,
    MAX_CODE_LENGTH,
    build_colab_prompt,
    call_gemini,
    check_memory,
)
from dcode.llm.parser import extract_json
from dcode.observability import write_log

app = Flask(__name__)
CORS(app)


@app.route("/agent", methods=["POST"])
def agent_endpoint():
    start_time = time.time()
    task = ""
    try:
        check_memory()
        payload = request.get_json(force=True) or {}
        task = (payload.get("task") or "").strip()
        code = payload.get("code", "") or ""

        if not task:
            return jsonify({"error": "Task field is required."}), 400
        if len(code) > MAX_CODE_LENGTH:
            return jsonify({"error": f"Code exceeds {MAX_CODE_LENGTH} chars."}), 400

        raw = call_gemini(build_colab_prompt(task, code))
        result = extract_json(raw) or {}
        summary = result.get("result", "")
        write_log("colab_agent", task, f"gemini({GEMINI_MODEL})", "success", summary)

        return jsonify({
            "success": True,
            "task": task,
            "model": GEMINI_MODEL,
            "plan": result.get("plan", []),
            "actions": result.get("actions", []),
            "result": summary,
            "raw": raw,
            "runtime_seconds": round(time.time() - start_time, 2),
        })
    except ColabAgentError as exc:
        write_log("colab_agent", task, "error", "fail", str(exc))
        return jsonify({"success": False, "error": str(exc)}), 500
    except Exception as exc:
        write_log("colab_agent", task, "unknown_error", "fail", str(exc))
        return jsonify({"success": False, "error": str(exc)}), 500


@app.route("/health", methods=["GET"])
def health_endpoint():
    mem = psutil.virtual_memory()
    return jsonify({
        "status": "healthy",
        "model": GEMINI_MODEL,
        "port": 5000,
        "free_memory_mb": mem.available // (1024 * 1024),
    })


def start_colab_server(port: int = 5000, use_ngrok: bool = True) -> None:
    if use_ngrok:
        from pyngrok import ngrok
        print(f"Public URL: {ngrok.connect(port, bind_tls=True).public_url}")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
