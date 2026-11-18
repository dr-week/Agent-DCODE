"""
High-level Orchestrator facade managing DCODE backend and Ollama services.
"""

import threading
import time
from typing import Any, Dict, Tuple
from dcode.config import BACKEND_PORT, OLLAMA_PORT, PROJECT_ROOT
from dcode.orchestrator.health import check_service_health, is_port_open
from dcode.orchestrator.lifecycle import (
    start_backend_service,
    start_ollama_service,
    stop_named_service,
)
from dcode.orchestrator.models import Service, ServiceStatus


class Orchestrator:
    """Manages local services (Flask Backend & Ollama) for DCODE."""

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.services: Dict[str, Service] = {
            "backend": Service(name="backend", port=BACKEND_PORT),
            "ollama": Service(name="ollama", port=OLLAMA_PORT),
        }
        self.project_root = PROJECT_ROOT
        self.backend_script = self.project_root / "scripts" / "run_web.py"
        self.health_check_interval = 5

    def log(self, message: str, level: str = "INFO") -> None:
        if self.verbose:
            print(f"[{level}] {message}")

    def is_port_open(self, port: int, timeout: float = 1.0) -> bool:
        return is_port_open(port, timeout)

    def check_service_health(self, service_name: str) -> Tuple[bool, str]:
        return check_service_health(self.services, service_name)

    def start_backend(self) -> bool:
        return start_backend_service(self.services, self.project_root, self.backend_script, self.log)

    def start_ollama(self) -> bool:
        return start_ollama_service(self.services, self.log)

    def start_all(self) -> bool:
        return self.start_backend() and self.start_ollama()

    def stop_service(self, service_name: str) -> bool:
        return stop_named_service(self.services, service_name, self.log)

    def stop_all(self) -> bool:
        return self.stop_service("backend") and self.stop_service("ollama")

    def restart_service(self, service_name: str) -> bool:
        self.stop_service(service_name)
        time.sleep(1)
        return self.start_backend() if service_name == "backend" else self.start_ollama()

    def get_status(self) -> Dict[str, Dict[str, Any]]:
        status: Dict[str, Dict[str, Any]] = {}
        for name, svc in self.services.items():
            ok, msg = self.check_service_health(name)
            status[name] = {
                "port": svc.port, "status": "running" if ok else "stopped", "healthy": ok,
                "pid": svc.pid, "message": msg,
                "uptime_seconds": (time.time() - svc.start_time) if svc.start_time else None,
            }
        return status

    def print_status(self) -> None:
        for name, info in self.get_status().items():
            sym = "[OK]" if info["healthy"] else "[XX]"
            print(f"{sym} {name.upper()} (port {info['port']}): {info['status']} - {info['message']}")

    def health_check_loop(self, interval: int = 5) -> None:
        while True:
            for name, svc in self.services.items():
                ok, _ = self.check_service_health(name)
                if not ok and svc.status == ServiceStatus.RUNNING:
                    self.restart_service(name)
            time.sleep(interval)

    def run_health_check_background(self) -> threading.Thread:
        t = threading.Thread(target=self.health_check_loop, daemon=True, args=(self.health_check_interval,))
        t.start()
        return t


def start_all() -> bool: return Orchestrator().start_all()
def stop_all() -> bool: return Orchestrator().stop_all()
def get_status() -> Dict[str, Dict[str, Any]]: return Orchestrator().get_status()
