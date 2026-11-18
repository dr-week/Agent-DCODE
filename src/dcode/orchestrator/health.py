"""
Port and HTTP health checks for DCODE local services.
"""

import socket
from typing import Dict, Tuple
import requests
from dcode.orchestrator.models import Service


def is_port_open(port: int, timeout: float = 1.0) -> bool:
    """Check if a TCP port is listening on localhost."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            return sock.connect_ex(("localhost", port)) == 0
    except Exception:
        return False


def check_service_health(services: Dict[str, Service], service_name: str) -> Tuple[bool, str]:
    """Check if backend or ollama service is responsive."""
    service = services.get(service_name)
    if not service or not service.port:
        return False, f"Unknown service: {service_name}"

    if not is_port_open(service.port):
        return False, f"Port {service.port} not responding"

    if service_name == "backend":
        try:
            res = requests.get(f"http://localhost:{service.port}/health", timeout=2)
            return res.status_code == 200, "Backend healthy"
        except Exception as e:
            return False, f"Backend health check failed: {e}"

    if service_name == "ollama":
        try:
            res = requests.get(f"http://localhost:{service.port}/api/tags", timeout=2)
            return res.status_code == 200, "Ollama healthy"
        except Exception as e:
            return False, f"Ollama health check failed: {e}"

    return True, "Port responding"
