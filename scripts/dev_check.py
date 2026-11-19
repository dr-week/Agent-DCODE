#!/usr/bin/env python3
"""
All-in-One Developer Quality Gate (<100 lines).
Executes modularity audit, all unit test suites, and quantitative SWE evaluations in one shot.
"""

from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def run_stage(name: str, cmd: list) -> bool:
    print(f"\n========================================\n[STAGE] {name}\n========================================")
    t0 = time.time()
    res = subprocess.run(cmd, cwd=ROOT)
    elapsed = round(time.time() - t0, 2)
    status = "PASSED" if res.returncode == 0 else "FAILED"
    print(f"[STAGE RESULT] {name}: {status} ({elapsed}s)")
    return res.returncode == 0


def main() -> None:
    t_start = time.time()
    stages = [
        ("Modularity Gate (<100 lines)", [sys.executable, "scripts/check_modularity.py"]),
        ("Static Analysis & Linters", [sys.executable, "scripts/lint.py"]),
        ("Unit Tests Suite", [sys.executable, "-m", "unittest", "discover", "-s", "tests"]),
        ("SWE Evals Benchmark", [sys.executable, "evals/run_evals.py"]),
    ]

    failed = []
    for name, cmd in stages:
        if not run_stage(name, cmd):
            failed.append(name)

    total_elapsed = round(time.time() - t_start, 2)
    print("\n========================================")
    print(f"[SUMMARY] Total Duration: {total_elapsed}s")
    if failed:
        print(f"[SUMMARY FAIL] {len(failed)} stages failed: {', '.join(failed)}")
        sys.exit(1)
    print("[SUMMARY PASS] All stages passed! Ready for PR/Commit.")
    sys.exit(0)


if __name__ == "__main__":
    main()
