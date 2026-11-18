"""
Process discovery and duplicate cleanup for DCODE services.
"""

from typing import Callable, List, Optional
import psutil


def get_process_by_port(port: int) -> Optional[psutil.Process]:
    """Find process listening on a given TCP port."""
    try:
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                for conn in proc.net_connections():
                    if conn.laddr.port == port:
                        return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception:
        pass
    return None


def get_duplicate_processes(service_name: str) -> List[psutil.Process]:
    """Find running processes matching backend or ollama."""
    duplicates: List[psutil.Process] = []
    if service_name == "backend":
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                if "python" in (proc.name() or "").lower():
                    cmdline = " ".join(proc.cmdline() or [])
                    if "web_app" in cmdline or "run_web" in cmdline or "dcode.web" in cmdline:
                        duplicates.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    elif service_name == "ollama":
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                if "ollama" in (proc.name() or "").lower():
                    duplicates.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    return duplicates


def kill_duplicate_processes(
    service_name: str, log_fn: Optional[Callable[[str, str], None]] = None
) -> int:
    """Kill all but the newest instance of a service."""
    duplicates = get_duplicate_processes(service_name)
    if len(duplicates) <= 1:
        return 0

    duplicates.sort(key=lambda p: p.create_time(), reverse=True)
    killed = 0
    for proc in duplicates[1:]:
        try:
            if log_fn:
                log_fn(f"Killing duplicate {service_name} process (PID {proc.pid})", "INFO")
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except psutil.TimeoutExpired:
                proc.kill()
            killed += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return killed
