#!/usr/bin/env python3
"""
AST RepoMap Auto-Sync Script (<100 lines).
Scans all Python, JS, and TS symbols and writes an updated repository map to docs/REPOMAP.md.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dcode.config import PROJECT_ROOT
from dcode.integrations import RepoMap


def sync_repomap() -> int:
    root = PROJECT_ROOT
    rm = RepoMap(str(root / "src"))
    markdown = rm.render_markdown(max_files=100)

    header = (
        "# Agent-DCODE Codebase Symbol Map\n\n"
        "Auto-generated via `scripts/repomap_sync.py` using AST and Tree-Sitter.\n"
        "Used by SWE agents and the Agent Harness to locate target symbols without overflowing context.\n\n"
        "---\n\n"
    )
    full_content = header + markdown
    out_file = root / "docs" / "REPOMAP.md"
    out_file.write_text(full_content, encoding="utf-8")

    symbols = rm.scan()
    total_syms = sum(len(v) for v in symbols.values())
    print(f"[REPOMAP SYNC] Scanned {len(symbols)} source files ({total_syms} symbols).")
    print(f"[REPOMAP SYNC] Updated {out_file.relative_to(root)}")
    return 0


if __name__ == "__main__":
    sys.exit(sync_repomap())
