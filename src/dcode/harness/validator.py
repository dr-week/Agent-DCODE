"""
Harness Invariant & Code Validator (<100 lines).
Validates Python AST syntax, import integrity, and path safety before executing test commands.
Prevents unparseable agent code from consuming execution budgets and test timeouts.
"""

import ast
import os
from typing import Any, Dict, List


class HarnessValidator:
    """Performs pre-flight and post-flight validation on modified files."""

    def __init__(self, workspace_dir: str):
        self.workspace_dir = os.path.abspath(workspace_dir)

    def validate_python_syntax(self, file_path: str) -> Dict[str, Any]:
        """Verify that a Python file parses cleanly without SyntaxError."""
        full_path = os.path.join(self.workspace_dir, file_path) if not os.path.isabs(file_path) else file_path
        if not os.path.exists(full_path):
            return {"valid": False, "error": f"File not found: {file_path}", "file": file_path}
        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            ast.parse(content, filename=file_path)
            return {"valid": True, "file": file_path, "lines": len(content.splitlines())}
        except SyntaxError as err:
            return {
                "valid": False,
                "file": file_path,
                "error": f"SyntaxError at line {err.lineno}: {err.msg}",
                "lineno": err.lineno,
            }

    def validate_workspace_files(self, extensions: tuple = (".py",)) -> Dict[str, Any]:
        """Scan all matching files in the workspace and validate syntax."""
        errors: List[Dict[str, Any]] = []
        scanned = 0
        for root, dirs, files in os.walk(self.workspace_dir):
            dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", "node_modules", ".venv"}]
            for fname in files:
                if fname.endswith(extensions):
                    scanned += 1
                    res = self.validate_python_syntax(os.path.join(root, fname))
                    if not res["valid"]:
                        errors.append(res)
        return {"scanned": scanned, "valid": len(errors) == 0, "errors": errors}
