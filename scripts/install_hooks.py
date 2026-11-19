#!/usr/bin/env python3
"""
Developer Tooling: Pre-Commit Hook Installer (<100 lines).
Installs local git pre-commit hook enforcing the <100L modularity gate and zero-emoji policy.
"""

import os
from pathlib import Path
import stat
import sys

ROOT = Path(__file__).resolve().parents[1]
HOOKS_DIR = ROOT / ".git" / "hooks"

HOOK_CONTENT = """#!/usr/bin/env bash
# Agent-DCODE Local Pre-Commit Quality Gate
set -e

echo "[HOOK] Running modularity gate (<100 lines)..."
python3 scripts/check_modularity.py

echo "[HOOK] Enforcing zero-emoji policy..."
if git diff --cached --name-only | grep -E '\\.(py|md)$' | xargs grep -Pn '[\\x{1F600}-\\x{1F64F}\\x{1F300}-\\x{1F5FF}\\x{1F680}-\\x{1F6FF}\\x{2600}-\\x{26FF}]' 2>/dev/null; then
    echo "[HOOK ERROR] Emoji detected in staged files. Emojis are strictly prohibited."
    exit 1
fi

echo "[HOOK PASS] All pre-commit checks passed."
exit 0
"""


def install_hooks() -> None:
    if not HOOKS_DIR.exists():
        print(f"[INSTALL SKIP] No .git/hooks directory found at {HOOKS_DIR}")
        return
    hook_path = HOOKS_DIR / "pre-commit"
    hook_path.write_text(HOOK_CONTENT, encoding="utf-8")
    current_mode = hook_path.stat().st_mode
    hook_path.chmod(current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print(f"[INSTALL OK] Installed executable pre-commit hook at {hook_path}")


if __name__ == "__main__":
    install_hooks()
