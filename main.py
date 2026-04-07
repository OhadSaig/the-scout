#!/usr/bin/env python3
"""
The Scout — Autonomous CRM Perfectionist
PDR: https://github.com/your-org/the-scout

Usage:
  python main.py status        # Show CRM health dashboard (no Claude call)
  python main.py deep-clean    # Run Utopian Deep Clean
  python main.py monitor       # Run Career Tracker (job-change detection)
"""

import sys
import argparse
from rich.console import Console

console = Console()


def main():
    parser = argparse.ArgumentParser(
        prog="scout",
        description="The Scout — Autonomous CRM Perfectionist",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  status      Print CRM health dashboard (no API call)
  deep-clean  Run the Utopian Deep Clean across the entire CRM
  monitor     Run the Career Tracker — detect job changes & fire alerts
        """,
    )
    parser.add_argument(
        "command",
        choices=["status", "deep-clean", "monitor"],
        help="Which Scout mode to run",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Use scripted mock responses — no API key required, no cost",
    )
    args = parser.parse_args()

    # Lazy import after argument parsing so --help is instant
    from agents.scout import ScoutAgent

    try:
        agent = ScoutAgent(dry_run=args.dry_run)

        if args.command == "status":
            agent.show_status()

        elif args.command == "deep-clean":
            agent.run_deep_clean()

        elif args.command == "monitor":
            agent.run_monitor()

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted.[/yellow]")
        sys.exit(0)
    except Exception as exc:
        console.print(f"\n[red bold]Error:[/red bold] {exc}")
        raise


if __name__ == "__main__":
    main()
