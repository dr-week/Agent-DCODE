"""
Pre-Flight Linter & AST Syntax Guard.
Validates Python AST, detecting compilation errors and malformed syntax before test runs.
"""

import ast
from pathlib import Path
from typing import Any, Dict, List, Optional


class LinterGuard:
    """Performs static syntax and AST sanity checks on Python files and code strings."""

    @staticmethod
    def check_code(code_str: str, filename: str = "<memory>") -> Dict[str, Any]:
        """Validate code string with AST parsing; returns error details if invalid."""
        errors: List[str] = []
        try:
            tree = ast.parse(code_str, filename=filename)
            compile(tree, filename=filename, mode="exec")
        except SyntaxError as e:
            errors.append(f"SyntaxError in {filename}:{e.lineno}:{e.offset} - {e.msg}")
        except Exception as e:
            errors.append(f"CompileError in {filename}: {str(e)}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "total_nodes": sum(1 for _ in ast.walk(tree)) if len(errors) == 0 else 0,
        }

    @staticmethod
    def check_file(file_path: str | Path) -> Dict[str, Any]:
        """Validate Python file on disk."""
        path = Path(file_path)
        if not path.is_file() or path.suffix != ".py":
            return {"valid": False, "errors": [f"Invalid python file path: {file_path}"], "total_nodes": 0}
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
            return LinterGuard.check_code(content, filename=str(path))
        except Exception as e:
            return {"valid": False, "errors": [str(e)], "total_nodes": 0}

    @staticmethod
    def check_workspace(workspace_dir: str | Path, max_files: int = 100) -> Dict[str, Any]:
        """Batch scan Python files in workspace for syntax errors."""
        root = Path(workspace_dir)
        results: Dict[str, List[str]] = {}
        scanned = 0
        for py_file in root.rglob("*.py"):
            if any(part in py_file.parts for part in {".git", "__pycache__", ".venv", "venv"}):
                continue
            res = LinterGuard.check_file(py_file)
            if not res["valid"]:
                results[str(py_file.relative_to(root))] = res["errors"]
            scanned += 1
            if scanned >= max_files:
                break
        return {"scanned": scanned, "clean": len(results) == 0, "failures": results}
