"""
Sandboxed file system tools (write, append, read, list_files).
"""

import os
from typing import Any, Dict, Optional
from dcode.config import PROJECTS_DIR

BASE_DIR = str(PROJECTS_DIR)


def safe_path(path: Optional[str]) -> Optional[str]:
    """Resolve a path safely inside the projects/ sandbox."""
    if not path:
        return None
    clean = path.replace("projects/", "", 1) if path.startswith("projects/") else path
    full = os.path.abspath(os.path.join(BASE_DIR, clean))
    return full if full.startswith(BASE_DIR) else None


def write_file(a: Dict[str, Any]) -> str:
    path = a.get("path")
    content = a.get("content", "")
    full = safe_path(path)
    if not full:
        return f"[BLOCKED PATH] {path}"

    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    return f"[CREATED] {full}"


def append_file(a: Dict[str, Any]) -> str:
    path = a.get("path")
    content = a.get("content", "").replace("\\n", "\n")
    full = safe_path(path)
    if not full:
        return f"[APPEND ERROR] {path}"

    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "a", encoding="utf-8") as f:
        f.write("\n" + content.strip())
    return f"[APPENDED] {full}"


def read_file(a: Dict[str, Any]) -> str:
    path = a.get("path")
    full = safe_path(path)
    if not full or not os.path.exists(full):
        return f"[READ ERROR] {path}"

    with open(full, "r", encoding="utf-8") as f:
        return f.read()


def list_files(a: Dict[str, Any]) -> str:
    path = a.get("path", "projects")
    max_depth = a.get("max_depth", 3)
    full = BASE_DIR if path == "projects" else safe_path(path)
    if not full or not os.path.isdir(full):
        return f"[LIST ERROR] {path}"

    output_lines = [f"[FILE TREE] {full}"]

    def _tree(directory: str, prefix: str = "", depth: int = 0) -> None:
        if depth > max_depth:
            return
        try:
            items = [i for i in sorted(os.listdir(directory)) if not i.startswith(".")]
            for idx, item in enumerate(items):
                sub = os.path.join(directory, item)
                is_last = idx == len(items) - 1
                output_lines.append(f"{prefix}{'+-- ' if is_last else '|-- '}{item}")
                if os.path.isdir(sub):
                    _tree(sub, prefix + ("    " if is_last else "|   "), depth + 1)
        except PermissionError:
            pass

    _tree(full)
    return "\n".join(output_lines)
