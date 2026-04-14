#!/usr/bin/env python3
"""
CLI wrapper for DCODE System Orchestrator
Simple command-line interface to manage local services
"""

import sys
import argparse
from orchestrator import Orchestrator


def main():
    parser = argparse.ArgumentParser(
        description="DCODE System Orchestrator - Manage local AI agent services",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  dcode start              # Start all services
  dcode stop               # Stop all services
  dcode status             # Show service status
  dcode restart            # Restart all services
  dcode restart --service backend   # Restart specific service
        """,
    )

    parser.add_argument(
        "command",
        choices=["start", "stop", "status", "restart"],
        help="Command to execute",
    )

    parser.add_argument(
        "--service",
        choices=["backend", "ollama"],
        help="Target specific service (use with restart)",
    )

    parser.add_argument(
        "--health-check",
        action="store_true",
        help="Enable continuous health monitoring",
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress verbose output",
    )

    args = parser.parse_args()

    orch = Orchestrator(verbose=not args.quiet)

    try:
        if args.command == "start":
            print("\n" + "=" * 70)
            print("  DCODE SYSTEM ORCHESTRATOR - START")
            print("=" * 70 + "\n")

            success = orch.start_all()

            if success and args.health_check:
                print("\n[INFO] Starting continuous health monitoring...")
                print("[INFO] Press Ctrl+C to stop\n")
                orch.run_health_check_background()
                try:
                    import time

                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n[INFO] Health monitoring stopped")

            sys.exit(0 if success else 1)

        elif args.command == "stop":
            print("\n" + "=" * 70)
            print("  DCODE SYSTEM ORCHESTRATOR - STOP")
            print("=" * 70 + "\n")

            success = orch.stop_all()
            sys.exit(0 if success else 1)

        elif args.command == "status":
            orch.print_status()
            sys.exit(0)

        elif args.command == "restart":
            print("\n" + "=" * 70)
            print("  DCODE SYSTEM ORCHESTRATOR - RESTART")
            print("=" * 70 + "\n")

            if args.service:
                success = orch.restart_service(args.service)
            else:
                import time

                print("[INFO] Stopping all services...")
                orch.stop_all()
                time.sleep(1)
                print("[INFO] Starting all services...")
                success = orch.start_all()

            sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n[WARN] Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
