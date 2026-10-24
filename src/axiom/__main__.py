"""Command-line interface for AXIOM."""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

from axiom import __version__
from axiom.interpreter import AxiomError, InterpreterRuntime, run_file


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="axiom",
        description="Run, check, or inspect readable AXIOM scientific programs.",
    )
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=f"AXIOM version {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: run
    run_parser = subparsers.add_parser("run", help="Execute an .ax script")
    run_parser.add_argument("file", help="Path to an .ax program")

    # Command: check
    check_parser = subparsers.add_parser("check", help="Check syntax and validity of an .ax script")
    check_parser.add_argument("file", help="Path to an .ax program")

    # Command: inspect
    inspect_parser = subparsers.add_parser("inspect", help="Inspect model and variables in an .ax script")
    inspect_parser.add_argument("file", help="Path to an .ax program")

    # Positional argument for default 'run' behavior
    parser.add_argument(
        "file_default",
        metavar="file",
        nargs="?",
        default=None,
        help="Path to an .ax program (default command: run)",
    )

    args = parser.parse_args(argv)

    command = args.command
    file_arg = getattr(args, "file", None) or getattr(args, "file_default", None)

    if command is None and file_arg is None:
        parser.print_help()
        return 0

    if command is None:
        command = "run"

    if file_arg is None:
        print("AXIOM error: No input file specified.", file=sys.stderr)
        return 1

    file_path = Path(file_arg)
    if not file_path.exists():
        print(f"AXIOM error: File not found: {file_path}", file=sys.stderr)
        return 1

    try:
        if command == "run":
            values = run_file(file_path)
            for value in values:
                if isinstance(value, float) and math.isfinite(value):
                    print(f"{value:g}")
                else:
                    print(value)

        elif command == "check":
            run_file(file_path)
            print(f"AXIOM check passed: {file_path}")

        elif command == "inspect":
            runtime = InterpreterRuntime()
            runtime.run_source(file_path.read_text(encoding="utf-8"))
            print(f"=== AXIOM Inspection Report: {file_path} ===")
            if runtime.neurons:
                print(f"Defined Neurons: {list(runtime.neurons.keys())}")
            else:
                print("Defined Neurons: None")
            print(f"Active Stimulus: {type(runtime.active_stimulus).__name__}")
            if runtime.last_result:
                print(f"Last Simulation Samples: {len(runtime.last_result.times_ms)}")
                print(f"Spike Count: {len(runtime.last_result.spike_times_ms)}")
            else:
                print("Last Simulation: None run")

    except AxiomError as error:
        print(f"AXIOM error: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
