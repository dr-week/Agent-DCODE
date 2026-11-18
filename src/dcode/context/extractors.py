"""
Context extractors for files, directories, and selected code snippets.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional
from dcode.config import PROJECTS_DIR


def get_file_context(file_path: str, max_lines: int = 50) -> Optional[Dict[str, Any]]:
    """Get context of a specific file inside projects/."""
    try:
        clean = file_path.replace("projects/", "", 1) if file_path.startswith("projects/") else file_path
        abs_path = PROJECTS_DIR / clean
        if not abs_path.exists():
            return None

        lines = abs_path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
        return {
            "filename": file_path,
            "lines": lines[:max_lines],
            "total_lines": len(lines),
            "truncated": len(lines) > max_lines,
            "type": Path(file_path).suffix,
        }
    except Exception as e:
        return {"error": str(e)}


def get_directory_context(dir_path: str = "projects", max_depth: int = 2) -> Optional[Dict[str, Any]]:
    """Get directory structure context."""
    try:
        abs_path = str(PROJECTS_DIR) if dir_path == "projects" else str(PROJECTS_DIR / dir_path)
        if not os.path.exists(abs_path):
            return None

        file_list = []
        for root, _, files in os.walk(abs_path):
            depth = root.replace(abs_path, "").count(os.sep)
            if depth > max_depth:
                continue
            for file in files[:10]:
                full_file = os.path.join(root, file)
                file_list.append({
                    "name": file,
                    "path": full_file.replace(abs_path, "").strip(os.sep),
                    "size": os.path.getsize(full_file),
                })

        return {"directory": dir_path, "files": file_list[:20], "file_count": len(file_list)}
    except Exception as e:
        return {"error": str(e)}


def get_selected_code_context(code: str, language: str = "python") -> Dict[str, Any]:
    """Get context from selected code snippet."""
    lines = code.strip().split("\n")
    return {
        "code": code[:1000],
        "language": language,
        "lines": len(lines),
        "truncated": len(code) > 1000,
    }
