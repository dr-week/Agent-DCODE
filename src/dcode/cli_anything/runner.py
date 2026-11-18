"""
CLI-Anything Harness Runner.
Discovers and executes agent-native CLIs with deterministic `--json` output and `--help` introspection.
"""

import json
import shutil
import subprocess
from typing import Any, Dict, List
from dcode.config import DEFAULT_TIMEOUT_SECONDS, PROJECTS_DIR


def discover_cli_harnesses() -> List[Dict[str, str]]:
    """Discover generated CLI-Anything scripts in projects/ and system PATH."""
    harnesses: List[Dict[str, str]] = []
    for path in sorted(PROJECTS_DIR.glob("cli_anything_*.py")):
        skill_md = path.with_suffix(".SKILL.md")
        harnesses.append({
            "name": path.stem.replace("_", "-"),
            "entrypoint": str(path.relative_to(PROJECTS_DIR)),
            "skill_doc": str(skill_md.relative_to(PROJECTS_DIR)) if skill_md.exists() else "",
        })
    return harnesses


def run_cli_harness(command: List[str], ensure_json: bool = True) -> Dict[str, Any]:
    """Execute a CLI-Anything command with `--json` flag and parse structured output."""
    cmd = list(command)
    if ensure_json and "--json" not in cmd and "--help" not in cmd:
        cmd.append("--json")

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(PROJECTS_DIR),
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT_SECONDS,
        )
        stdout = proc.stdout.strip()
        parsed_json = None
        try:
            parsed_json = json.loads(stdout)
        except json.JSONDecodeError:
            pass

        return {
            "success": proc.returncode == 0,
            "exit_code": proc.returncode,
            "command": " ".join(cmd),
            "data": parsed_json,
            "raw_stdout": stdout,
            "stderr": proc.stderr.strip(),
        }
    except Exception as e:
        return {"success": False, "exit_code": -1, "command": " ".join(cmd), "error": str(e)}


def check_binary_available(binary_name: str) -> bool:
    """Check if an external cli-anything binary is on PATH."""
    return shutil.which(binary_name) is not None
