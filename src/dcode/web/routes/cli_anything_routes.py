"""
CLI-Anything Web API endpoints (/api/cli-anything/*).
Exposes CLI harness discovery, generation, execution, and session undo over REST.
"""

from flask import Blueprint, jsonify, request
from dcode.cli_anything import (
    discover_cli_harnesses,
    generate_cli_anything_harness,
    get_session_status,
    run_cli_harness,
    undo_last_mutation,
)

cli_anything_bp = Blueprint("cli_anything", __name__)


@cli_anything_bp.route("/api/cli-anything/harnesses", methods=["GET"])
def list_harnesses():
    harnesses = discover_cli_harnesses()
    return jsonify({"harnesses": harnesses, "count": len(harnesses)})


@cli_anything_bp.route("/api/cli-anything/generate", methods=["POST"])
def generate_harness():
    data = request.json or {}
    path = data.get("path", "").strip()
    if not path:
        return jsonify({"success": False, "error": "Target 'path' is required"}), 400
    res = generate_cli_anything_harness(path)
    return jsonify(res), (200 if res.get("success") else 400)


@cli_anything_bp.route("/api/cli-anything/run", methods=["POST"])
def execute_harness():
    data = request.json or {}
    command = data.get("command", [])
    if isinstance(command, str):
        command = command.split()
    if not command:
        return jsonify({"success": False, "error": "'command' list or string required"}), 400
    return jsonify(run_cli_harness(command))


@cli_anything_bp.route("/api/cli-anything/session", methods=["GET"])
def session_status():
    return jsonify(get_session_status())


@cli_anything_bp.route("/api/cli-anything/undo", methods=["POST"])
def session_undo():
    return jsonify(undo_last_mutation())
