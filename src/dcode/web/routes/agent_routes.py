"""
Codex & Autonomous Agent execution routes (/api/agent/*).
"""

import time
from flask import Blueprint, jsonify, request
from dcode.agents.autonomous import run_autonomous_agent
from dcode.agents.codex import execute_task
from dcode.context.builder import prepare_agent_context
from dcode.observability import write_log
from dcode.web.state import agent_log

agent_bp = Blueprint("agent", __name__)


@agent_bp.route("/api/agent/execute", methods=["POST"])
def agent_execute():
    data = request.json or {}
    task = data.get("task", "").strip()
    if not task:
        return jsonify({"error": "Task is required"}), 400

    try:
        start_time = time.time()
        context = prepare_agent_context(
            task=task,
            selected_code=data.get("selected_code"),
            active_file=data.get("active_file"),
        )
        result = execute_task(task, context)
        execution_time = time.time() - start_time

        status = "success" if result.get("success") else "fail"
        details = result.get("error") or f"{len(result.get('actions', []))} actions executed"
        write_log("web_api", task, "agent_execute", status, details)

        agent_log.append({
            "task": task,
            "success": result.get("success"),
            "time": execution_time,
            "actions_count": len(result.get("actions", [])),
        })

        return jsonify({
            "success": result.get("success"),
            "task": task,
            "plan": result.get("plan", []),
            "actions_count": len(result.get("actions", [])),
            "actions": result.get("actions", []),
            "results": result.get("results", []),
            "error": result.get("error"),
            "execution_time": round(execution_time, 2),
        })
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@agent_bp.route("/api/agent/autonomous", methods=["POST"])
def agent_autonomous():
    data = request.json or {}
    goal = data.get("goal", "").strip()
    if not goal:
        return jsonify({"error": "Goal is required"}), 400
    max_iter = int(data.get("max_iterations", 5))
    res = run_autonomous_agent(goal=goal, max_iterations=max_iter, context=data.get("context", ""))
    return jsonify(res)


@agent_bp.route("/api/agent/log", methods=["GET"])
def agent_log_endpoint():
    return jsonify({"log": agent_log})


@agent_bp.route("/api/agent/clear", methods=["POST"])
def agent_clear():
    agent_log.clear()
    return jsonify({"message": "Agent log cleared"})
