"""
Real-time transparency tracking routes (/api/transparency/*).
"""

from flask import Blueprint, jsonify, request
from dcode.observability import create_new_session, get_tracker

transparency_bp = Blueprint("transparency", __name__)


@transparency_bp.route("/api/transparency/session", methods=["POST"])
def transparency_start_session():
    data = request.json or {}
    tracker = create_new_session()
    tracker.start_execution(data.get("task", ""), data.get("plan_steps", []))
    return jsonify({"session_id": tracker.session_id, "status": "started", "state": tracker.get_state()})


@transparency_bp.route("/api/transparency/state", methods=["GET"])
def transparency_get_state():
    return jsonify({"state": get_tracker().get_state()})


@transparency_bp.route("/api/transparency/plan", methods=["POST"])
def transparency_add_plan():
    data = request.json or {}
    tracker = get_tracker()
    tracker.add_plan(data.get("steps", []), data.get("estimated_time", 0))
    return jsonify({"status": "plan_added", "state": tracker.get_state()})


@transparency_bp.route("/api/transparency/step/start", methods=["POST"])
def transparency_start_step():
    data = request.json or {}
    tracker = get_tracker()
    tracker.start_step(data.get("step_index", 0), data.get("step_name", ""))
    return jsonify({"status": "step_started", "state": tracker.get_state()})


@transparency_bp.route("/api/transparency/step/complete", methods=["POST"])
def transparency_complete_step():
    data = request.json or {}
    tracker = get_tracker()
    tracker.complete_step(data.get("output", ""), data.get("success", True))
    return jsonify({"status": "step_completed", "state": tracker.get_state()})


@transparency_bp.route("/api/transparency/action", methods=["POST"])
def transparency_add_action():
    data = request.json or {}
    tracker = get_tracker()
    tracker.add_action(data.get("action", {}))
    return jsonify({
        "status": "action_added",
        "action_index": len(tracker.actions) - 1,
        "state": tracker.get_state(),
    })


@transparency_bp.route("/api/transparency/action/<int:action_index>/complete", methods=["POST"])
def transparency_complete_action(action_index: int):
    data = request.json or {}
    tracker = get_tracker()
    tracker.complete_action(action_index, data.get("output", ""), data.get("success", True))
    return jsonify({"status": "action_completed", "state": tracker.get_state()})


@transparency_bp.route("/api/transparency/error", methods=["POST"])
def transparency_report_error():
    data = request.json or {}
    tracker = get_tracker()
    tracker.add_error(data.get("error", ""), data.get("context", ""))
    return jsonify({"status": "error_recorded", "state": tracker.get_state()})


@transparency_bp.route("/api/transparency/complete", methods=["POST"])
def transparency_complete_execution():
    data = request.json or {}
    tracker = get_tracker()
    tracker.complete_execution(data.get("success", True))
    return jsonify({"status": "execution_completed", "state": tracker.get_state()})
