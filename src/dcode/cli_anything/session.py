"""
CLI-Anything Stateful Session Manager (arXiv:2606.03854).
Provides first-class session.json state, trajectory history, and file Undo/Redo snapshots.
"""

import json
from datetime import datetime
from typing import Any, Dict, Optional
from dcode.config import LOGS_DIR
from dcode.tools.file_tools import safe_path

SESSION_FILE = LOGS_DIR / "cli_anything_session.json"


def _load_session() -> Dict[str, Any]:
    if SESSION_FILE.exists():
        try:
            return json.loads(SESSION_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"active_project": "default", "undo_stack": [], "redo_stack": [], "trajectory": []}


def _save_session(state: Dict[str, Any]) -> None:
    SESSION_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def record_snapshot(file_path: str, command: str) -> None:
    """Save file snapshot before mutation so agents can run `undo`."""
    full = safe_path(file_path)
    state = _load_session()
    prev_content: Optional[str] = None
    existed = False
    if full:
        from pathlib import Path
        p = Path(full)
        existed = p.exists()
        if existed:
            prev_content = p.read_text(encoding="utf-8", errors="replace")

    state["undo_stack"].append({
        "timestamp": datetime.now().isoformat(),
        "path": file_path,
        "existed": existed,
        "content": prev_content,
        "command": command,
    })
    state["undo_stack"] = state["undo_stack"][-20:]
    state["trajectory"].append({"timestamp": datetime.now().isoformat(), "command": command, "path": file_path})
    _save_session(state)


def undo_last_mutation() -> Dict[str, Any]:
    """Revert the most recent file mutation from the undo stack."""
    from pathlib import Path
    state = _load_session()
    if not state["undo_stack"]:
        return {"success": False, "message": "Undo stack is empty"}

    snap = state["undo_stack"].pop()
    full = safe_path(snap["path"])
    if not full:
        return {"success": False, "message": f"Invalid path: {snap['path']}"}

    target = Path(full)
    if not snap["existed"] and target.exists():
        target.unlink()
    elif snap["existed"] and snap["content"] is not None:
        target.write_text(snap["content"], encoding="utf-8")

    state["redo_stack"].append(snap)
    _save_session(state)
    return {"success": True, "restored_path": snap["path"], "undone_command": snap["command"]}


def get_session_status() -> Dict[str, Any]:
    """Return inspectable CLI-Anything session state."""
    state = _load_session()
    return {
        "active_project": state.get("active_project", "default"),
        "undo_depth": len(state.get("undo_stack", [])),
        "redo_depth": len(state.get("redo_stack", [])),
        "recent_trajectory": state.get("trajectory", [])[-5:],
    }
