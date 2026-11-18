"""
Action execution and goal completion verifier.
Checks tool failure markers rather than false-positive substring matches on code content.
"""

from typing import Any, Dict, List, Optional
from dcode.cli_anything.session import record_snapshot
from dcode.tools.executor import execute_actions

FAILURE_PREFIXES = (
    "[BLOCKED PATH]",
    "[APPEND ERROR]",
    "[READ ERROR]",
    "[EDIT ERROR]",
    "[SEARCH ERROR]",
    "[LIST ERROR]",
    "[CMD ERROR]",
    "[PYTHON ERROR]",
    "[PYTHON TIMEOUT]",
    "[BASH ERROR]",
    "[BASH TIMEOUT]",
    "[JS ERROR]",
    "[JS TIMEOUT]",
    "[PROCESS ERROR]",
    "[UNKNOWN ACTION]",
    "[ERROR in",
    "[TIMEOUT]",
)


def execute_and_verify(actions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Record CLI-Anything undo snapshots, execute actions, and verify outputs."""
    result: Dict[str, Any] = {
        "success": True,
        "actions_count": len(actions),
        "outputs": [],
        "error": None,
    }
    try:
        for act in actions:
            if act.get("type") in ("write_file", "create_file", "append_file", "replace_in_file"):
                if act.get("path"):
                    record_snapshot(act["path"], act["type"])

        exec_results = execute_actions(actions)
        result["outputs"] = exec_results

        errors = []
        for item in exec_results:
            out = str(item.get("output", "")).strip()
            if out.startswith(FAILURE_PREFIXES) or "Traceback (most recent call last):" in out:
                errors.append(out[:200])

        if errors:
            result["success"] = False
            result["error"] = "; ".join(errors)
    except Exception as e:
        result["success"] = False
        result["error"] = str(e)

    return result


def check_goal_complete(
    execution_result: Dict[str, Any], success_criteria: Optional[str] = None
) -> bool:
    """Verify whether the execution result satisfies completion criteria."""
    if not execution_result.get("success"):
        return False
    outputs = execution_result.get("outputs", [])
    if not outputs:
        return False

    combined = "\n".join(str(o.get("output", "")) for o in outputs)
    indicators = ("[CREATED]", "[UPDATED]", "[APPENDED]", "success", "complete", "done", "✅")
    if any(ind.lower() in combined.lower() for ind in indicators):
        return True

    return bool(success_criteria) and execution_result.get("success", False)
