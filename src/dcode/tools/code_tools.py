"""
Subprocess-isolated code and command execution tools (Python, Bash, JS).
Replaces unsafe in-process exec() with sandboxed subprocess execution in projects/.
"""

import subprocess
import sys
from typing import Any, Dict
from dcode.config import DEFAULT_TIMEOUT_SECONDS
from dcode.tools.file_tools import BASE_DIR


def run_cmd(a: Dict[str, Any]) -> str:
    cmd = (a.get("command") or "").replace("\\\\", "\\")
    if not cmd:
        return "[CMD ERROR] No command provided"
    try:
        r = subprocess.run(
            cmd, shell=True, cwd=BASE_DIR, capture_output=True, text=True, timeout=DEFAULT_TIMEOUT_SECONDS
        )
        return f"{r.stdout}\n{r.stderr}".strip() if r.stderr else r.stdout
    except subprocess.TimeoutExpired:
        return "[TIMEOUT]"


def run_python(a: Dict[str, Any]) -> str:
    """Execute Python code in an isolated subprocess instead of host exec()."""
    code = a.get("code", "")
    if not code:
        return "[PYTHON ERROR] No code provided"
    try:
        r = subprocess.run(
            [sys.executable, "-c", code],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT_SECONDS,
        )
        if r.returncode != 0:
            return f"[PYTHON ERROR] {r.stderr.strip() or r.stdout.strip()}"
        return r.stdout
    except subprocess.TimeoutExpired:
        return "[PYTHON TIMEOUT]"
    except Exception as e:
        return f"[PYTHON ERROR] {e}"


def run_bash(a: Dict[str, Any]) -> str:
    cmd = a.get("command", "")
    if not cmd:
        return "[BASH ERROR] No command provided"
    try:
        r = subprocess.run(
            cmd, shell=True, cwd=BASE_DIR, capture_output=True, text=True, timeout=DEFAULT_TIMEOUT_SECONDS
        )
        output = r.stdout
        if r.stderr:
            output += f"\n[STDERR] {r.stderr}"
        return output
    except subprocess.TimeoutExpired:
        return "[BASH TIMEOUT]"
    except Exception as e:
        return f"[BASH ERROR] {e}"


def run_js(a: Dict[str, Any]) -> str:
    code = a.get("code", "")
    if not code:
        return "[JS ERROR] No code provided"
    try:
        r = subprocess.run(["node", "-e", code], cwd=BASE_DIR, capture_output=True, text=True, timeout=10)
        return f"{r.stdout}\n[JS ERROR] {r.stderr}".strip() if r.stderr else r.stdout
    except FileNotFoundError:
        return "[JS ERROR] Node.js not installed"
    except subprocess.TimeoutExpired:
        return "[JS TIMEOUT]"
