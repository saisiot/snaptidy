#!/usr/bin/env python3
"""
SnapTidy CLI - Command line interface for organizing and deduplicating files.
"""

import argparse
import os
import sys
from typing import List, Optional
import logging

from rich.console import Console
from rich.logging import RichHandler

from . import flatten
from . import dedup
from . import organize
from . import utils


console = Console()


def setup_logging(log_file: Optional[str] = None, verbose: bool = False) -> None:
    """Configure logging for the application."""
    log_level = logging.DEBUG if verbose else logging.INFO

    # Configure rich handler for console output
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, console=console)],
    )

    # Add file handler if log file specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        logging.getLogger().addHandler(file_handler)


def flatten_command(args) -> None:
    """Handle the flatten subcommand."""
    flatten.run(path=args.path, dry_run=args.dry_run)


def dedup_command(args) -> None:
    """Handle the dedup subcommand."""
    dedup.run(
        path=args.path,
        sensitivity=args.sensitivity,
        dry_run=args.dry_run,
        threads=args.threads,
    )


def organize_command(args) -> None:
    """Handle the organize subcommand."""
    organize.run(path=args.path, date_format=args.date_format, dry_run=args.dry_run)


def parse_args(args: List[str]) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="SnapTidy - A CLI tool for organizing files and removing duplicates."
    )

    # Common arguments for all subcommands
    parser.add_argument(
        "--path",
        default=os.getcwd(),
        help="Target directory path (default: current directory)",
    )
    parser.add_argument("--log", help="Log output to specified file")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    # Create subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Flatten subcommand
    flatten_parser = subparsers.add_parser(
        "flatten", help="Move all files from subdirectories into the current directory"
    )
    flatten_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    flatten_parser.set_defaults(func=flatten_command)

    # Dedup subcommand
    dedup_parser = subparsers.add_parser("dedup", help="Remove duplicate files")
    dedup_parser.add_argument(
        "--sensitivity",
        type=float,
        default=0.9,
        help="Sensitivity for perceptual similarity detection (0.0-1.0)",
    )
    dedup_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    dedup_parser.add_argument(
        "--threads",
        type=int,
        default=os.cpu_count(),
        help=f"Number of threads to use (default: {os.cpu_count()})",
    )
    dedup_parser.set_defaults(func=dedup_command)

    # Organize subcommand
    organize_parser = subparsers.add_parser("organize", help="Organize files by date")
    organize_parser.add_argument(
        "--date-format",
        choices=["year", "yearmonth"],
        default="year",
        help="Format for date-based folder organization",
    )
    organize_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    organize_parser.set_defaults(func=organize_command)

    return parser.parse_args(args)


def main() -> int:
    """Main entry point for the CLI."""
    args = parse_args(sys.argv[1:])

    # Set up logging
    setup_logging(args.log, args.verbose)

    try:
        if args.command is None:
            console.print("[bold red]Error:[/] No command specified.")
            console.print("Run 'snaptidy --help' for usage information.")
            return 1

        # Execute the appropriate subcommand
        args.func(args)
        return 0

    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/]")
        return 130
    except Exception as e:
        logging.exception(f"An error occurred: {str(e)}")
        console.print(f"[bold red]Error:[/] {str(e)}")
        if args.verbose:
            console.print_exception()
        return 1


if __name__ == "__main__":
    sys.exit(main())
