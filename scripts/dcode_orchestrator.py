#!/usr/bin/env python3
"""
CLI wrapper for DCODE System Orchestrator.
Manages local Backend and Ollama services.
"""

import argparse
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dcode.orchestrator import Orchestrator


def main() -> None:
    parser = argparse.ArgumentParser(
        description="DCODE System Orchestrator - Manage local AI agent services"
    )
    parser.add_argument("command", choices=["start", "stop", "status", "restart"])
    parser.add_argument("--service", choices=["backend", "ollama"], help="Target specific service")
    parser.add_argument("--health-check", action="store_true", help="Enable continuous health monitoring")
    parser.add_argument("--quiet", action="store_true", help="Suppress verbose output")
    args = parser.parse_args()

    orch = Orchestrator(verbose=not args.quiet)

    try:
        if args.command == "start":
            success = orch.start_all()
            if success and args.health_check:
                orch.run_health_check_background()
                while True:
                    time.sleep(1)
            sys.exit(0 if success else 1)

        if args.command == "stop":
            sys.exit(0 if orch.stop_all() else 1)

        if args.command == "status":
            orch.print_status()
            sys.exit(0)

        if args.command == "restart":
            if args.service:
                success = orch.restart_service(args.service)
            else:
                orch.stop_all()
                time.sleep(1)
                success = orch.start_all()
            sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n[WARN] Interrupted by user")
        sys.exit(1)


if __name__ == "__main__":
    main()
