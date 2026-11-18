"""
CLI-Anything 7-Phase Pipeline Generator (HKUDS/CLI-Anything pattern).
Analyzes Python modules in projects/ via AST and generates an Agent-Native CLI + SKILL.md.
"""

import ast
from pathlib import Path
from typing import Any, Dict, List
from dcode.cli_anything.skill_doc import generate_skill_markdown
from dcode.tools.file_tools import safe_path


def analyze_python_module(source_path: Path) -> List[Dict[str, Any]]:
    """Phase 1 (Analyze): Parse public functions and arguments using Python AST."""
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    functions: List[Dict[str, Any]] = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
            args = [a.arg for a in node.args.args if a.arg != "self"]
            functions.append({
                "name": node.name,
                "args": args,
                "doc": (ast.get_docstring(node) or "").splitlines()[0] if ast.get_docstring(node) else "",
            })
    return functions


def build_cli_harness_code(module_stem: str, functions: List[Dict[str, Any]]) -> str:
    """Phase 2 & 3 (Design & Implement): Build a self-contained CLI with --json and --dry-run."""
    fn_names = [f["name"] for f in functions]
    return f'''#!/usr/bin/env python3
"""Auto-generated CLI-Anything harness for {module_stem}."""
import argparse, json, sys
import {module_stem} as target

FUNCTIONS = {fn_names!r}

def main():
    parser = argparse.ArgumentParser(description="CLI-Anything harness for {module_stem}")
    parser.add_argument("command", choices=FUNCTIONS + ["status"], help="Function to invoke")
    parser.add_argument("args", nargs="*", help="Positional arguments (auto-cast int/float/str)")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Emit structured JSON")
    parser.add_argument("--dry-run", action="store_true", help="Preview call without executing")
    ns = parser.parse_args()

    def _cast(v):
        for fn in (int, float):
            try: return fn(v)
            except ValueError: pass
        return v

    cast_args = [_cast(a) for a in ns.args]
    if ns.dry_run:
        res = {{"status": "dry_run", "command": ns.command, "args": cast_args}}
    elif ns.command == "status":
        res = {{"status": "ready", "module": "{module_stem}", "commands": FUNCTIONS}}
    else:
        out = getattr(target, ns.command)(*cast_args)
        res = {{"status": "ok", "command": ns.command, "result": out}}

    print(json.dumps(res) if ns.as_json else f"[{{res['status'].upper()}}] {{res}}")

if __name__ == "__main__":
    main()
'''


def generate_cli_anything_harness(target_rel_path: str) -> Dict[str, Any]:
    """Run the CLI-Anything generation pipeline on a target Python file in projects/."""
    full = safe_path(target_rel_path)
    if not full or not Path(full).exists():
        return {"success": False, "error": f"Target file not found: {target_rel_path}"}

    src = Path(full)
    functions = analyze_python_module(src)
    cli_name = f"cli_anything_{src.stem}.py"
    cli_path = src.parent / cli_name
    skill_path = src.parent / f"cli_anything_{src.stem}.SKILL.md"

    cli_path.write_text(build_cli_harness_code(src.stem, functions), encoding="utf-8")
    skill_path.write_text(generate_skill_markdown(src.stem, cli_name, functions), encoding="utf-8")

    return {
        "success": True,
        "source": src.name,
        "cli_harness": cli_name,
        "skill_manifest": skill_path.name,
        "commands_exposed": [f["name"] for f in functions] + ["status"],
    }
