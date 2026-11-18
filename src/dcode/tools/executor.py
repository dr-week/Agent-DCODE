"""
Central action dispatcher mapping structured action types to tool handlers.
"""

from typing import Any, Callable, Dict, List
from dcode.tools.code_tools import run_bash, run_cmd, run_js, run_python
from dcode.tools.edit_tools import replace_in_file, search_code
from dcode.tools.file_tools import append_file, list_files, read_file, write_file
from dcode.tools.system_tools import get_processes, show_progress

ACTION_HANDLERS: Dict[str, Callable[[Dict[str, Any]], str]] = {
    "write_file": write_file,
    "create_file": write_file,
    "append_file": append_file,
    "edit_file": append_file,
    "replace_in_file": replace_in_file,
    "read_file": read_file,
    "search_code": search_code,
    "list_files": list_files,
    "run_command": run_cmd,
    "execute_cmd": run_bash,
    "run_bash": run_bash,
    "run_python": run_python,
    "run_code": run_python,
    "run_js": run_js,
    "get_processes": get_processes,
    "show_progress": show_progress,
}


def execute_actions(actions: List[Dict[str, Any]], dry_run: bool = False) -> List[Dict[str, Any]]:
    """Execute a list of structured agent actions and capture outputs."""
    results: List[Dict[str, Any]] = []
    for action in actions:
        action_type = action.get("type", "")
        handler = ACTION_HANDLERS.get(action_type)

        if dry_run:
            output = f"[DRY-RUN] Would execute {action_type}: {action.get('path') or action.get('command', '')}"
        elif not handler:
            output = f"[UNKNOWN ACTION] {action_type}"
        else:
            try:
                output = handler(action)
            except Exception as e:
                output = f"[ERROR in {action_type}] {e}"

        result = action.copy()
        result["output"] = output
        results.append(result)

    return results
