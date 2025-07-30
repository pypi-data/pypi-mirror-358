#!/usr/bin/env python3
"""
Eion CLI

Command-line interface for Eion server management.
"""

import sys
import argparse
from typing import List

from .client import EionClient
from .exceptions import EionError


def setup_command(args) -> int:
    """Setup Eion server infrastructure"""
    try:
        client = EionClient()
        client.setup(force_reset=args.force)
        return 0
    except EionError as e:
        print(f"Setup failed: {e}")
        return 1


def run_command(args) -> int:
    """Run Eion server"""
    try:
        client = EionClient()
        client.run(detached=args.detached)
        return 0
    except EionError as e:
        print(f"Run failed: {e}")
        return 1


def stop_command(args) -> int:
    """Stop Eion server"""
    try:
        client = EionClient()
        client.stop()
        return 0
    except EionError as e:
        print(f"Stop failed: {e}")
        return 1


def reset_command(args) -> int:
    """Reset Eion to clean state"""
    try:
        client = EionClient()
        client.reset()
        return 0
    except EionError as e:
        print(f"Reset failed: {e}")
        return 1


def health_command(args) -> int:
    """Check Eion server health"""
    try:
        client = EionClient()
        if client.server_health():
            print("✅ Eion server is healthy")
            return 0
        else:
            print("❌ Eion server is not responding")
            return 1
    except EionError as e:
        print(f"Health check failed: {e}")
        return 1


def main(argv: List[str] = None) -> int:
    """Main CLI entry point"""
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description="Eion - Shared memory storage for AI agent systems",
        prog="eion"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Setup Eion server infrastructure")
    setup_parser.add_argument(
        "--force", 
        action="store_true", 
        help="Force reset configuration even if it exists"
    )
    setup_parser.set_defaults(func=setup_command)

    # Run command
    run_parser = subparsers.add_parser("run", help="Run Eion server")
    run_parser.add_argument(
        "--detached", 
        action="store_true", 
        help="Run server in background"
    )
    run_parser.set_defaults(func=run_command)

    # Stop command
    stop_parser = subparsers.add_parser("stop", help="Stop Eion server")
    stop_parser.set_defaults(func=stop_command)

    # Reset command
    reset_parser = subparsers.add_parser("reset", help="Reset Eion to clean state")
    reset_parser.set_defaults(func=reset_command)

    # Health command
    health_parser = subparsers.add_parser("health", help="Check Eion server health")
    health_parser.set_defaults(func=health_command)

    # Parse arguments
    args = parser.parse_args(argv)

    if not hasattr(args, 'func'):
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main()) 