"""
Project file tree and active file tracking endpoints (/api/files, /api/current-file).
"""

import os
from typing import Any, Dict, List
from flask import Blueprint, jsonify, request
from dcode.config import PROJECT_ROOT
from dcode.web.state import current_file_state

file_bp = Blueprint("files", __name__)

IGNORE_PATTERNS = {
    ".git", "__pycache__", ".venv", "node_modules", ".logs", ".pytest_cache", ".DS_Store"
}


def _build_tree(root_path: str, prefix: str = "") -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    try:
        entries = [
            e for e in sorted(os.listdir(root_path))
            if e not in IGNORE_PATTERNS and not e.endswith(".pyc")
        ]
        for entry in entries:
            full_path = os.path.join(root_path, entry)
            rel_path = os.path.join(prefix, entry) if prefix else entry
            if os.path.isdir(full_path):
                items.append({
                    "name": entry,
                    "path": rel_path,
                    "type": "directory",
                    "children": _build_tree(full_path, rel_path),
                })
            else:
                try:
                    items.append({
                        "name": entry,
                        "path": rel_path,
                        "type": "file",
                        "size": os.path.getsize(full_path),
                    })
                except OSError:
                    pass
    except PermissionError:
        pass
    return items


@file_bp.route("/api/files", methods=["GET"])
def get_project_files():
    try:
        root = str(PROJECT_ROOT)
        return jsonify({"success": True, "files": _build_tree(root), "root": "."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@file_bp.route("/api/current-file", methods=["GET"])
def get_current_file():
    return jsonify(current_file_state)


@file_bp.route("/api/current-file", methods=["POST"])
def set_current_file():
    data = request.json or {}
    current_file_state["path"] = data.get("path", current_file_state["path"])
    current_file_state["status"] = data.get("status", "pending")
    current_file_state["message"] = data.get("message", "")
    return jsonify({"success": True, "state": current_file_state})
