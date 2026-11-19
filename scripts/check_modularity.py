#!/usr/bin/env python3
"""
Modularity Enforcer (<100 lines).
Scans all Python files across src/, scripts/, tests/, and evals/ to enforce the strict
< 100 lines per file constraint. Warns on files approaching the threshold (>85 lines).
"""

import glob
from pathlib import Path
import sys

TARGET_PATTERNS = ["src/**/*.py", "scripts/**/*.py", "tests/**/*.py", "evals/**/*.py"]
MAX_LINES = 100
WARN_THRESHOLD = 85


def check_modularity() -> int:
    violators = []
    watchlist = []
    total_files = 0
    total_lines = 0

    root = Path(__file__).resolve().parents[1]
    for pattern in TARGET_PATTERNS:
        for p in glob.glob(str(root / pattern), recursive=True):
            total_files += 1
            rel = Path(p).relative_to(root)
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                lines = sum(1 for _ in f)
            total_lines += lines
            if lines >= MAX_LINES:
                violators.append((rel, lines))
            elif lines >= WARN_THRESHOLD:
                watchlist.append((rel, lines))

    print(f"[MODULARITY AUDIT] Scanned {total_files} Python files ({total_lines} total lines)")
    if watchlist:
        print(f"[WATCHLIST] {len(watchlist)} files approaching limit (>={WARN_THRESHOLD} lines):")
        for rel, count in sorted(watchlist, key=lambda x: x[1], reverse=True):
            print(f"  - {rel}: {count} lines")

    if violators:
        print(f"[FAIL] {len(violators)} files violate the < {MAX_LINES} lines rule:")
        for rel, count in violators:
            print(f"  * {rel}: {count} lines (MUST BE < {MAX_LINES})")
        return 1

    print(f"[PASS] 100% of codebase files are strictly < {MAX_LINES} lines.")
    return 0


if __name__ == "__main__":
    sys.exit(check_modularity())
