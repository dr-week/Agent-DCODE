"""
System monitoring and progress tools (get_processes, show_progress).
"""

import time
from typing import Any, Dict


def get_processes(a: Dict[str, Any]) -> str:
    """Get system process information sorted by CPU or memory."""
    sort_by = a.get("sort_by", "memory")
    limit = a.get("limit", 10)
    output_lines = ["[PROCESSES]", "PID\tName\tCPU%\tMEM%"]

    try:
        import psutil
        processes = []
        for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        key = "cpu_percent" if sort_by == "cpu" else "memory_percent"
        processes.sort(key=lambda x: x.get(key, 0) or 0, reverse=True)

        for p in processes[:limit]:
            name = (p.get("name") or "")[:10]
            cpu = p.get("cpu_percent", 0) or 0.0
            mem = p.get("memory_percent", 0) or 0.0
            output_lines.append(f"{p['pid']}\t{name}\t{cpu:.1f}\t{mem:.1f}")

        return "\n".join(output_lines)
    except Exception as e:
        return f"[PROCESS ERROR] {e}"


def show_progress(a: Dict[str, Any]) -> str:
    """Render an ASCII progress bar."""
    steps = int(a.get("steps", 10))
    delay = float(a.get("delay", 0.05))
    output_lines = [f"[PROGRESS] Running {steps} steps..."]

    for i in range(steps + 1):
        percent = (i / max(steps, 1)) * 100
        filled = int(percent / 2)
        bar = "█" * filled + "░" * (50 - filled)
        output_lines.append(f"[{bar}] {percent:.0f}%")
        time.sleep(min(delay, 0.2))

    output_lines.append("[PROGRESS COMPLETE]")
    return "\n".join(output_lines)
