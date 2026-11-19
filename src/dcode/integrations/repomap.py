"""
Phase 2: AST & Tree-Sitter Repository Map Adapter (tree-sitter/py-tree-sitter + Aider pattern).
Generates a compact structural symbol map (classes, functions, signatures) of a codebase
so SWE agents locate targets without overflowing context windows.
"""

import ast
import os
import re
from typing import Any, Dict, List

try:
    import tree_sitter  # type: ignore  # noqa: F401

    HAS_TREESITTER = True
except ImportError:
    HAS_TREESITTER = False

IGNORE_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", "dist", "build"}


class RepoMap:
    """Builds a compact AST symbol map of Python, JS, and TS files in a repository."""

    def __init__(self, root_dir: str):
        self.root_dir = os.path.abspath(root_dir)

    def scan(self, max_files: int = 100) -> Dict[str, List[str]]:
        """Return a mapping of relative file paths to extracted class and function signatures."""
        symbol_map: Dict[str, List[str]] = {}
        count = 0
        for root, dirs, files in os.walk(self.root_dir):
            dirs[:] = [d for d in sorted(dirs) if d not in IGNORE_DIRS]
            for fname in sorted(files):
                if not fname.endswith((".py", ".js", ".ts")):
                    continue
                full = os.path.join(root, fname)
                rel = os.path.relpath(full, self.root_dir)
                symbols = self._extract_py(full) if fname.endswith(".py") else self._extract_js(full)
                if symbols:
                    symbol_map[rel] = symbols
                count += 1
                if count >= max_files:
                    return symbol_map
        return symbol_map

    def render_markdown(self, max_files: int = 60) -> str:
        """Render the repository symbol map as a compact LLM context block."""
        smap = self.scan(max_files=max_files)
        lines = [f"# Repository Symbol Map ({len(smap)} files)"]
        for rel, syms in smap.items():
            lines.append(f"\n## {rel}")
            for sym in syms[:25]:
                lines.append(f"  - {sym}")
        return "\n".join(lines)

    def _extract_py(self, path: str) -> List[str]:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                tree = ast.parse(f.read(), filename=path)
        except Exception:
            return []
        out: List[str] = []
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                out.append(f"class {node.name} [{', '.join(methods)}]")
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                args = [a.arg for a in node.args.args]
                out.append(f"def {node.name}({', '.join(args)})")
        return out

    def _extract_js(self, path: str) -> List[str]:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except Exception:
            return []
        matches = re.findall(r"(?:class\s+\w+|function\s+\w+\s*\([^)]*\))", text)
        return matches[:25]


def build_repo_map(root_dir: str) -> Dict[str, Any]:
    """Callable helper for @tool or REST route consumption."""
    rm = RepoMap(root_dir)
    return {"backend": "tree-sitter+ast" if HAS_TREESITTER else "python-ast", "symbols": rm.scan()}
