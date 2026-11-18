"""
Chat & health routes (/api/ask, /api/history, /api/clear, /api/status, /health).
"""

from typing import Any, Dict
from flask import Blueprint, jsonify, request
from dcode.config import OLLAMA_MODEL
from dcode.llm.ollama_client import ask_llm
from dcode.llm.parser import extract_json
from dcode.tools.executor import execute_actions
from dcode.web.state import chat_history

chat_bp = Blueprint("chat", __name__)


def run_single_prompt_agent(user_input: str) -> Dict[str, Any]:
    """Run the prompt agent with up to 3 retry attempts."""
    for attempt in range(3):
        try:
            response = ask_llm(user_input)
            data = extract_json(response)
            if data:
                actions = data.get("actions", [])
                results = execute_actions(actions)
                return {"success": True, "actions": results, "raw": response}
        except Exception as e:
            print(f"[ATTEMPT {attempt + 1} ERROR]", str(e))

    return {"success": False, "error": "Could not get valid JSON after 3 attempts"}


@chat_bp.route("/api/ask", methods=["POST"])
def api_ask():
    data = request.json or {}
    user_input = data.get("message", "").strip()
    if not user_input:
        return jsonify({"error": "Empty message"}), 400

    chat_history.append({"role": "user", "content": user_input})
    result = run_single_prompt_agent(user_input)
    response_msg = (
        f"Executed {len(result.get('actions', []))} actions"
        if result["success"]
        else result.get("error", "Unknown error")
    )
    chat_history.append({"role": "assistant", "content": response_msg})

    return jsonify({
        "success": result["success"],
        "message": response_msg,
        "details": result,
        "history": chat_history,
    })


@chat_bp.route("/api/history", methods=["GET"])
def api_history():
    return jsonify({"history": chat_history})


@chat_bp.route("/api/clear", methods=["POST"])
def api_clear():
    chat_history.clear()
    return jsonify({"message": "Chat history cleared"})


@chat_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "backend"}), 200


@chat_bp.route("/api/status", methods=["GET"])
def api_status():
    return jsonify({
        "status": "online",
        "model": OLLAMA_MODEL,
        "messages": len(chat_history),
    })
