"""
Service startup and shutdown lifecycle helpers for Backend and Ollama.
"""

from pathlib import Path
import platform
import subprocess
import sys
import time
from typing import Callable, Dict
import psutil
from dcode.orchestrator.health import check_service_health, is_port_open
from dcode.orchestrator.models import Service, ServiceStatus
from dcode.orchestrator.processes import get_duplicate_processes, kill_duplicate_processes


def start_backend_service(
    services: Dict[str, Service], project_root: Path, backend_script: Path, log_fn: Callable[[str, str], None]
) -> bool:
    health_ok, _ = check_service_health(services, "backend")
    if health_ok:
        log_fn("Backend already running", "INFO")
        services["backend"].status = ServiceStatus.RUNNING
        return True

    log_fn("Starting backend service...", "INFO")
    kill_duplicate_processes("backend", log_fn)
    flags = subprocess.CREATE_NEW_PROCESS_GROUP if platform.system() == "Windows" else 0
    proc = subprocess.Popen(
        [sys.executable, str(backend_script)],
        cwd=str(project_root), stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=flags,
    )
    for _ in range(10):
        time.sleep(1)
        if is_port_open(services["backend"].port or 5000):
            s = services["backend"]
            s.process, s.pid, s.status, s.start_time = proc, proc.pid, ServiceStatus.RUNNING, time.time()
            log_fn(f"Backend started (PID {proc.pid})", "INFO")
            return True
    log_fn("Backend failed to start", "ERROR")
    proc.terminate()
    return False


def start_ollama_service(services: Dict[str, Service], log_fn: Callable[[str, str], None]) -> bool:
    health_ok, _ = check_service_health(services, "ollama")
    if health_ok:
        log_fn("Ollama already running", "INFO")
        services["ollama"].status = ServiceStatus.RUNNING
        return True

    log_fn("Starting Ollama service...", "INFO")
    kill_duplicate_processes("ollama", log_fn)
    try:
        res = subprocess.run(["ollama", "--version"], capture_output=True, timeout=5)
        if res.returncode != 0:
            log_fn("Ollama not installed or not in PATH", "ERROR")
            return False
        flags = subprocess.CREATE_NEW_PROCESS_GROUP if platform.system() == "Windows" else 0
        proc = subprocess.Popen(["ollama", "serve"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=flags)
        for _ in range(15):
            time.sleep(1)
            if is_port_open(services["ollama"].port or 11434):
                s = services["ollama"]
                s.process, s.pid, s.status, s.start_time = proc, proc.pid, ServiceStatus.RUNNING, time.time()
                log_fn(f"Ollama started (PID {proc.pid})", "INFO")
                return True
        proc.terminate()
    except Exception as e:
        log_fn(f"Error starting Ollama: {e}", "ERROR")
    return False


def stop_named_service(services: Dict[str, Service], service_name: str, log_fn: Callable[[str, str], None]) -> bool:
    service = services.get(service_name)
    if not service:
        return False
    log_fn(f"Stopping {service_name}...", "INFO")
    for proc in get_duplicate_processes(service_name):
        try:
            proc.terminate()
            proc.wait(timeout=3)
        except psutil.TimeoutExpired:
            proc.kill()
        except Exception:
            pass
    service.status, service.process, service.pid = ServiceStatus.STOPPED, None, None
    return True
