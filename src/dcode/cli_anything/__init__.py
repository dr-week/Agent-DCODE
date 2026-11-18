"""
CLI-Anything integration package for Agent-DCODE.
"""

from dcode.cli_anything.generator import generate_cli_anything_harness
from dcode.cli_anything.runner import discover_cli_harnesses, run_cli_harness
from dcode.cli_anything.session import (
    get_session_status,
    record_snapshot,
    undo_last_mutation,
)

__all__ = [
    "discover_cli_harnesses",
    "generate_cli_anything_harness",
    "get_session_status",
    "record_snapshot",
    "run_cli_harness",
    "undo_last_mutation",
]
