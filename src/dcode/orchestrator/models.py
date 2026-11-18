"""
Data models for the DCODE Service Orchestrator.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional
import psutil


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
