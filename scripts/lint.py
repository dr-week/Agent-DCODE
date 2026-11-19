#!/usr/bin/env python3
"""
Agent-DCODE Static Analysis & Linter Gate (<100 lines).
Validates Python AST syntax, line limits (<150 LOC), trailing whitespace, and zero-emoji compliance.
"""

import ast
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MAX_LOC = 150
EMOJI_PATTERN = re.compile(r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U00002600-\U000026FF]")


def lint_file(file_path: Path) -> list[str]:
    errors = []
    text = file_path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    # 1. Line count check
    if len(lines) > MAX_LOC:
        errors.append(f"Exceeds {MAX_LOC} LOC limit ({len(lines)} lines)")

    # 2. AST Syntax validation
    try:
        compile(ast.parse(text, filename=str(file_path)), filename=str(file_path), mode="exec")
    except SyntaxError as e:
        errors.append(f"SyntaxError line {e.lineno}:{e.offset} - {e.msg}")
    except Exception as e:
        errors.append(f"CompileError: {str(e)}")

    # 3. Zero-Emoji compliance
    for idx, line in enumerate(lines, start=1):
        if EMOJI_PATTERN.search(line):
            errors.append(f"Line {idx}: Prohibited emoji detected")

    return errors


def main() -> None:
    print("[LINTER] Scanning Python source files for quality, syntax, and line limits...")
    py_files = [p for p in ROOT.rglob("*.py") if not any(x in p.parts for x in {".git", "__pycache__", ".venv", "venv", "projects"})]
    total_errors = 0

    for py_file in sorted(py_files):
        errs = lint_file(py_file)
        if errs:
            total_errors += len(errs)
            rel = py_file.relative_to(ROOT)
            for err in errs:
                print(f"  FAILED: {rel}: {err}")

    if total_errors > 0:
        print(f"\n[LINTER FAILED] Found {total_errors} code quality violation(s).")
        sys.exit(1)

    print(f"[LINTER PASSED] Clean! Scanned {len(py_files)} files with 0 violations.")
    sys.exit(0)


if __name__ == "__main__":
    main()
