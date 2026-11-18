"""
Surgical code editing and search tools inspired by SWE-agent ACI and Aider.
"""

import os
import re
from typing import Any, Dict
from dcode.tools.file_tools import BASE_DIR, safe_path


def replace_in_file(a: Dict[str, Any]) -> str:
    """Replace an exact target snippet inside a file in projects/."""
    path = a.get("path")
    target = a.get("target", "")
    replacement = a.get("replacement", "")
    full = safe_path(path)

    if not full or not os.path.exists(full):
        return f"[EDIT ERROR] File not found: {path}"
    if not target:
        return "[EDIT ERROR] Non-empty 'target' string is required"

    with open(full, "r", encoding="utf-8") as f:
        content = f.read()
    if target not in content:
        return f"[EDIT ERROR] Target block not found in {path}"

    updated = content.replace(target, replacement, 1)
    with open(full, "w", encoding="utf-8") as f:
        f.write(updated)
    return f"[UPDATED] {full}"


def search_code(a: Dict[str, Any]) -> str:
    """Search for a regex or substring pattern across files in projects/."""
    pattern = a.get("pattern", "")
    subpath = a.get("path", "projects")
    if not pattern:
        return "[SEARCH ERROR] Pattern required"

    root_dir = BASE_DIR if subpath == "projects" else safe_path(subpath)
    if not root_dir or not os.path.exists(root_dir):
        return f"[SEARCH ERROR] Invalid path: {subpath}"

    matches = []
    regex = re.compile(pattern)
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.startswith(".") or file.endswith(".pyc"):
                continue
            full_path = os.path.join(root, file)
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    for lineno, line in enumerate(f, 1):
                        if regex.search(line):
                            rel = os.path.relpath(full_path, BASE_DIR)
                            matches.append(f"{rel}:{lineno}: {line.strip()}")
                            if len(matches) >= 50:
                                return "\n".join(matches)
            except OSError:
                continue

    return "\n".join(matches) if matches else f"[NO MATCHES] {pattern}"
