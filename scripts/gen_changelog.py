#!/usr/bin/env python3
"""
Developer Tooling: Automated Semantic Changelog Generator (<100 lines).
Parses git log history and groups commits into structured markdown release notes.
"""

from collections import defaultdict
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def get_git_commits(limit: int = 40) -> list[tuple[str, str]]:
    cmd = ["git", "log", f"-n{limit}", "--format=%h|%s"]
    res = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if res.returncode != 0:
        return []
    commits = []
    for line in res.stdout.strip().splitlines():
        if "|" in line:
            h, msg = line.split("|", 1)
            commits.append((h.strip(), msg.strip()))
    return commits


def categorize_commits(commits: list[tuple[str, str]]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = defaultdict(list)
    for h, msg in commits:
        prefix = msg.split(":")[0].lower() if ":" in msg else "other"
        clean_type = prefix.split("(")[0].strip()
        item = f"- [`{h}`] {msg}"
        if clean_type in {"feat", "feature"}:
            groups["Features"].append(item)
        elif clean_type in {"fix", "bugfix"}:
            groups["Bug Fixes"].append(item)
        elif clean_type in {"docs", "doc"}:
            groups["Documentation"].append(item)
        elif clean_type in {"test", "tests"}:
            groups["Testing & Verification"].append(item)
        else:
            groups["Maintenance & Chores"].append(item)
    return groups


def main() -> None:
    commits = get_git_commits()
    groups = categorize_commits(commits)
    print("# Release Changelog & Development Summary\n")
    for category in ["Features", "Bug Fixes", "Testing & Verification", "Documentation", "Maintenance & Chores"]:
        items = groups.get(category, [])
        if items:
            print(f"## {category}")
            for it in items:
                print(it)
            print()


if __name__ == "__main__":
    main()
