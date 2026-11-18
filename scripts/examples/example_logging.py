#!/usr/bin/env python3
"""
Example: Using the structured logging system in Agent-DCODE.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from dcode.observability import (
    clear_logs,
    format_log_summary,
    get_context_for_project,
    get_last_state,
    read_logs,
    write_log,
)


def example_basic_logging() -> None:
    print("\n=== Example 1: Basic Logging ===")
    entry = write_log(
        project="example_project",
        task="Generate Python function",
        action="llm_call",
        status="success",
        details="Created function with 42 lines",
    )
    print(f"Logged entry: {entry}")

    write_log(
        project="example_project",
        task="Build API endpoint",
        action="execute",
        status="fail",
        details="Port 5000 already in use",
    )
    for log in read_logs("example_project")[-3:]:
        print(f"  {log['timestamp']}: {log['task']} - {log['status']}")


def example_context_and_summary() -> None:
    print("\n=== Example 2: Context Recovery & Summary ===")
    last = get_last_state("example_project")
    if last:
        print(f"Last state: {last['action']} - {last['status']}")

    for entry in get_context_for_project("example_project", limit=3):
        print(f"  - {entry['task'][:50]}")

    print(format_log_summary("example_project"))


def example_resumption() -> None:
    print("\n=== Example 3: Agent Resumption ===")
    write_log("learning_agent", "Tutorial", "fetch_resources", "success", "Got 250 resources")
    write_log("learning_agent", "Tutorial", "process", "fail", "Processed 100/250")
    last = get_last_state("learning_agent")
    if last:
        print(f"Resume from: {last['action']} ({last['details']})")


if __name__ == "__main__":
    example_basic_logging()
    example_context_and_summary()
    example_resumption()
    clear_logs("example_project")
    clear_logs("learning_agent")
    print("\n Demo logs cleaned up")
