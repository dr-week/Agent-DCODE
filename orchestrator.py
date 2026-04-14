"""
Local Development Orchestrator
Manages startup, shutdown, and health of backend + model services
"""

import os
import sys
import json
import time
import socket
import psutil
import subprocess
import platform
import threading
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path


class ServiceStatus(Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class Service:
    name: str
    port: Optional[int] = None
    process: Optional[psutil.Process] = None
    status: ServiceStatus = ServiceStatus.UNKNOWN
    pid: Optional[int] = None
    start_time: Optional[float] = None
    last_health_check: Optional[float] = None


class Orchestrator:
    """
    Manages all local services for DCODE agent system.
    Handles: Backend (Flask), Model Server (Ollama)
    """

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.services: Dict[str, Service] = {
            "backend": Service(name="backend", port=5000),
            "ollama": Service(name="ollama", port=11434),
        }
        self.project_root = Path(__file__).parent
        self.backend_script = self.project_root / "web_app.py"
        self.health_check_interval = 5  # seconds

    def log(self, message: str, level: str = "INFO"):
        """Log with timestamp"""
        if self.verbose:
            print(f"[{level}] {message}")

    def is_port_open(self, port: int, timeout: float = 1.0) -> bool:
        """Check if port is listening"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                result = sock.connect_ex(("localhost", port))
                return result == 0
        except Exception:
            return False

    def check_service_health(self, service_name: str) -> Tuple[bool, str]:
        """
        Check if service is responsive
        Returns: (is_healthy, message)
        """
        service = self.services.get(service_name)
        if not service:
            return False, f"Unknown service: {service_name}"

        # Check port
        if not self.is_port_open(service.port):
            return False, f"Port {service.port} not responding"

        # Try actual health endpoint
        if service_name == "backend":
            try:
                import requests

                response = requests.get(
                    f"http://localhost:{service.port}/health",
                    timeout=2,
                )
                return response.status_code == 200, "Backend healthy"
            except Exception as e:
                return False, f"Backend health check failed: {e}"

        elif service_name == "ollama":
            try:
                import requests

                response = requests.get(
                    f"http://localhost:{service.port}/api/tags",
                    timeout=2,
                )
                return response.status_code == 200, "Ollama healthy"
            except Exception as e:
                return False, f"Ollama health check failed: {e}"

        return self.is_port_open(service.port), "Port responding"

    def get_process_by_port(self, port: int) -> Optional[psutil.Process]:
        """Find process listening on port"""
        try:
            for proc in psutil.process_iter(["pid", "name", "connections"]):
                try:
                    for conn in proc.connections():
                        if conn.laddr.port == port:
                            return proc
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            self.log(f"Error finding process: {e}", "WARN")
        return None

    def get_duplicate_processes(self, service_name: str) -> List[psutil.Process]:
        """Find duplicate processes for service"""
        duplicates = []

        if service_name == "backend":
            # Look for python processes running web_app.py
            for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                try:
                    if "python" in proc.name().lower():
                        cmdline = " ".join(proc.cmdline())
                        if "web_app" in cmdline:
                            duplicates.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

        elif service_name == "ollama":
            # Look for ollama processes
            for proc in psutil.process_iter(["pid", "name"]):
                try:
                    if "ollama" in proc.name().lower():
                        duplicates.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

        return duplicates

    def kill_duplicate_processes(self, service_name: str) -> int:
        """Kill all but one instance of service"""
        duplicates = self.get_duplicate_processes(service_name)
        if len(duplicates) <= 1:
            return 0

        # Keep the newest one
        duplicates.sort(key=lambda p: p.create_time(), reverse=True)
        killed = 0

        for proc in duplicates[1:]:
            try:
                self.log(f"Killing duplicate {service_name} process (PID {proc.pid})")
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                except psutil.TimeoutExpired:
                    proc.kill()
                killed += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                self.log(f"Could not kill process: {e}", "WARN")

        return killed

    def start_backend(self) -> bool:
        """Start Flask backend"""
        try:
            # Check if already running
            health_ok, msg = self.check_service_health("backend")
            if health_ok:
                self.log("Backend already running")
                self.services["backend"].status = ServiceStatus.RUNNING
                return True

            self.log("Starting backend service...")

            # Kill duplicates first
            self.kill_duplicate_processes("backend")

            # Start new process
            python_exe = sys.executable
            proc = subprocess.Popen(
                [python_exe, str(self.backend_script)],
                cwd=str(self.project_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                if platform.system() == "Windows"
                else 0,
            )

            # Wait for service to be ready
            max_retries = 10
            for i in range(max_retries):
                time.sleep(1)
                if self.is_port_open(5000):
                    self.services["backend"].process = proc
                    self.services["backend"].pid = proc.pid
                    self.services["backend"].status = ServiceStatus.RUNNING
                    self.services["backend"].start_time = time.time()
                    self.log(f"Backend started (PID {proc.pid})")
                    return True

            self.log("Backend failed to start", "ERROR")
            proc.terminate()
            return False

        except Exception as e:
            self.log(f"Error starting backend: {e}", "ERROR")
            return False

    def start_ollama(self) -> bool:
        """Start Ollama model server"""
        try:
            # Check if already running
            health_ok, msg = self.check_service_health("ollama")
            if health_ok:
                self.log("Ollama already running")
                self.services["ollama"].status = ServiceStatus.RUNNING
                return True

            self.log("Starting Ollama service...")

            # Kill duplicates first
            self.kill_duplicate_processes("ollama")

            # Check if ollama is available
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                timeout=5,
            )
            if result.returncode != 0:
                self.log("Ollama not installed or not in PATH", "ERROR")
                return False

            # Start ollama serve
            proc = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                if platform.system() == "Windows"
                else 0,
            )

            # Wait for service to be ready
            max_retries = 15
            for i in range(max_retries):
                time.sleep(1)
                if self.is_port_open(11434):
                    self.services["ollama"].process = proc
                    self.services["ollama"].pid = proc.pid
                    self.services["ollama"].status = ServiceStatus.RUNNING
                    self.services["ollama"].start_time = time.time()
                    self.log(f"Ollama started (PID {proc.pid})")
                    return True

            self.log("Ollama failed to start", "ERROR")
            proc.terminate()
            return False

        except FileNotFoundError:
            self.log("Ollama executable not found in PATH", "ERROR")
            return False
        except Exception as e:
            self.log(f"Error starting Ollama: {e}", "ERROR")
            return False

    def start_all(self) -> bool:
        """Start all services"""
        self.log("=" * 60)
        self.log("Starting DCODE System Services")
        self.log("=" * 60)

        # Start backend
        backend_ok = self.start_backend()

        # Start ollama
        ollama_ok = self.start_ollama()

        self.log("=" * 60)
        if backend_ok and ollama_ok:
            self.log("All services started successfully!")
            self.log("Backend: http://localhost:5000")
            self.log("Ollama: http://localhost:11434")
            return True
        else:
            self.log("Some services failed to start", "ERROR")
            return False

    def stop_service(self, service_name: str) -> bool:
        """Stop individual service"""
        service = self.services.get(service_name)
        if not service:
            self.log(f"Unknown service: {service_name}", "ERROR")
            return False

        self.log(f"Stopping {service_name}...")

        try:
            # Find and kill all related processes
            if service_name == "backend":
                for proc in self.get_duplicate_processes("backend"):
                    try:
                        proc.terminate()
                        proc.wait(timeout=3)
                    except psutil.TimeoutExpired:
                        proc.kill()

            elif service_name == "ollama":
                for proc in self.get_duplicate_processes("ollama"):
                    try:
                        proc.terminate()
                        proc.wait(timeout=3)
                    except psutil.TimeoutExpired:
                        proc.kill()

            service.status = ServiceStatus.STOPPED
            service.process = None
            service.pid = None
            self.log(f"{service_name} stopped")
            return True

        except Exception as e:
            self.log(f"Error stopping {service_name}: {e}", "ERROR")
            return False

    def stop_all(self) -> bool:
        """Stop all services"""
        self.log("=" * 60)
        self.log("Stopping DCODE System Services")
        self.log("=" * 60)

        backend_ok = self.stop_service("backend")
        ollama_ok = self.stop_service("ollama")

        self.log("=" * 60)
        return backend_ok and ollama_ok

    def get_status(self) -> Dict[str, Dict]:
        """Get status of all services"""
        status = {}

        for service_name, service in self.services.items():
            # Check health
            health_ok, msg = self.check_service_health(service_name)

            status[service_name] = {
                "port": service.port,
                "status": "running" if health_ok else "stopped",
                "healthy": health_ok,
                "pid": service.pid,
                "message": msg,
                "uptime_seconds": (
                    time.time() - service.start_time
                    if service.start_time
                    else None
                ),
            }

        return status

    def print_status(self):
        """Print formatted status"""
        status = self.get_status()
        print("\n" + "=" * 60)
        print("DCODE System Status")
        print("=" * 60)

        for service_name, info in status.items():
            symbol = "[OK]" if info["healthy"] else "[XX]"
            print(f"\n{symbol} {service_name.upper()}")
            print(f"  Port: {info['port']}")
            print(f"  Status: {info['status']}")
            print(f"  PID: {info['pid']}")
            print(f"  Message: {info['message']}")
            if info["uptime_seconds"]:
                print(f"  Uptime: {info['uptime_seconds']:.0f}s")

        print("\n" + "=" * 60 + "\n")

    def restart_service(self, service_name: str) -> bool:
        """Restart a service"""
        self.log(f"Restarting {service_name}...")
        self.stop_service(service_name)
        time.sleep(1)

        if service_name == "backend":
            return self.start_backend()
        elif service_name == "ollama":
            return self.start_ollama()

        return False

    def health_check_loop(self, interval: int = 5):
        """Continuous health monitoring"""
        self.log(f"Starting health check loop (interval: {interval}s)")

        while True:
            try:
                for service_name, service in self.services.items():
                    health_ok, msg = self.check_service_health(service_name)

                    if not health_ok and service.status == ServiceStatus.RUNNING:
                        self.log(f"{service_name} is unresponsive: {msg}", "WARN")
                        # Attempt restart
                        self.log(f"Attempting to restart {service_name}...")
                        self.restart_service(service_name)

                time.sleep(interval)

            except KeyboardInterrupt:
                self.log("Health check stopped")
                break
            except Exception as e:
                self.log(f"Error in health check: {e}", "ERROR")
                time.sleep(interval)

    def run_health_check_background(self):
        """Start health check in background thread"""
        thread = threading.Thread(
            target=self.health_check_loop, daemon=True, args=(self.health_check_interval,)
        )
        thread.start()
        return thread


# Convenience functions
def start_all() -> bool:
    """Start all services"""
    orch = Orchestrator()
    return orch.start_all()


def stop_all() -> bool:
    """Stop all services"""
    orch = Orchestrator()
    return orch.stop_all()


def get_status() -> Dict[str, Dict]:
    """Get system status"""
    orch = Orchestrator()
    return orch.get_status()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="DCODE System Orchestrator")
    parser.add_argument(
        "command",
        choices=["start", "stop", "status", "restart"],
        help="Command to execute",
    )
    parser.add_argument(
        "--service",
        choices=["backend", "ollama"],
        help="Specific service (for restart)",
    )
    parser.add_argument(
        "--health-check",
        action="store_true",
        help="Run continuous health checks",
    )

    args = parser.parse_args()

    orch = Orchestrator()

    if args.command == "start":
        success = orch.start_all()
        if args.health_check:
            orch.run_health_check_background()
            print("\nHealth check running. Press Ctrl+C to stop.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
        sys.exit(0 if success else 1)

    elif args.command == "stop":
        success = orch.stop_all()
        sys.exit(0 if success else 1)

    elif args.command == "status":
        orch.print_status()
        sys.exit(0)

    elif args.command == "restart":
        if args.service:
            success = orch.restart_service(args.service)
            sys.exit(0 if success else 1)
        else:
            success = orch.stop_all()
            time.sleep(1)
            success = success and orch.start_all()
            sys.exit(0 if success else 1)
