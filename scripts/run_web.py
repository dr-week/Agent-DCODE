#!/usr/bin/env python3
"""
Entrypoint script to launch the Agent-DCODE Flask Web Server.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dcode.web.app import run_server

if __name__ == "__main__":
    run_server()
