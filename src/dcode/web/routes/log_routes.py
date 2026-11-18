"""
Project structured logging routes (/api/logs, /api/logs/<project>).
"""

from flask import Blueprint, jsonify
from dcode.config import LOGS_DIR
from dcode.observability import format_log_summary, read_logs

log_bp = Blueprint("logs", __name__)


@log_bp.route("/api/logs/<project>", methods=["GET"])
def get_project_logs(project: str):
    logs = read_logs(project)
    return jsonify({"project": project, "logs": logs, "count": len(logs)})


@log_bp.route("/api/logs/<project>/summary", methods=["GET"])
def get_project_summary(project: str):
    summary = format_log_summary(project)
    return jsonify({"project": project, "summary": summary})


@log_bp.route("/api/logs", methods=["GET"])
def list_all_logs():
    projects = [f.stem for f in sorted(LOGS_DIR.glob("*.json"))]
    return jsonify({"projects": projects, "count": len(projects)})
