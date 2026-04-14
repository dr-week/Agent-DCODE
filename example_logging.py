#!/usr/bin/env python
"""
Example: Using the structured logging system.
Demonstrates how to read logs, get context, and track project state.
"""

from logger import (
    write_log,
    read_logs,
    get_last_state,
    get_context_for_project,
    format_log_summary,
    clear_logs
)


def example_basic_logging():
    """Example 1: Basic logging"""
    print("\n=== Example 1: Basic Logging ===")
    
    # Log a successful task
    entry = write_log(
        project="example_project",
        task="Generate Python function",
        action="llm_call",
        status="success",
        details="Created function with 42 lines"
    )
    print(f"Logged entry: {entry}")
    
    # Log a failed task
    write_log(
        project="example_project",
        task="Build API endpoint",
        action="execute",
        status="fail",
        details="Port 5000 already in use"
    )
    
    # View all logs
    logs = read_logs("example_project")
    print(f"\nTotal logs: {len(logs)}")
    for log in logs[-3:]:  # Show last 3
        print(f"  {log['timestamp']}: {log['task']} - {log['status']}")


def example_context_recovery():
    """Example 2: Recover context for a project"""
    print("\n=== Example 2: Context Recovery ===")
    
    # Get last state
    last = get_last_state("example_project")
    if last:
        print(f"Last state: {last['action']} - {last['status']}")
    
    # Get recent context
    context = get_context_for_project("example_project", limit=3)
    print(f"Recent context ({len(context)} entries):")
    for entry in context:
        print(f"  - {entry['task'][:50]}")


def example_formatted_summary():
    """Example 3: Formatted summary"""
    print("\n=== Example 3: Formatted Summary ===")
    summary = format_log_summary("example_project")
    print(summary)


def example_multiple_projects():
    """Example 4: Multiple projects"""
    print("\n=== Example 4: Multiple Projects ===")
    
    # Log for different projects
    write_log("project_a", "Task 1", "execute", "success", "OK")
    write_log("project_b", "Task 2", "execute", "fail", "Timeout")
    write_log("project_c", "Task 3", "execute", "success", "OK")
    
    # List all
    for project in ["project_a", "project_b", "project_c"]:
        logs = read_logs(project)
        print(f"{project}: {len(logs)} entries")


def example_agent_resumption():
    """Example 5: Resume agent after interruption"""
    print("\n=== Example 5: Agent Resumption ===")
    
    # Simulate interrupted task
    write_log(
        "learning_agent",
        "Complete Python tutorial",
        "fetch_resources",
        "success",
        "Got 250 resources"
    )
    
    write_log(
        "learning_agent",
        "Complete Python tutorial",
        "process_resources",
        "fail",
        "Memory limit exceeded - processed 100/250"
    )
    
    # Resume: check what was done
    last = get_last_state("learning_agent")
    print(f"Last action: {last['action']}")
    print(f"Status: {last['status']}")
    print(f"Details: {last['details']}")
    print("\n→ Agent can resume processing remaining 150 resources")


if __name__ == "__main__":
    print("📋 Structured Logging System Examples")
    print("=" * 50)
    
    example_basic_logging()
    example_context_recovery()
    example_formatted_summary()
    example_multiple_projects()
    example_agent_resumption()
    
    # Cleanup
    clear_logs()
    print("\n✅ Logs cleared (demo only)")
