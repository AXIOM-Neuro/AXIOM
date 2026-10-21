
"""Command-line interface for AXIOM."""

import argparse
import math
import sys

from axiom.interpreter import AxiomError, run_file


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="axiom",
        description="Run a readable AXIOM scientific program.",
    )
    parser.add_argument("file", help="Path to an .ax program")
    args = parser.parse_args()

    try:
        values = run_file(args.file)

        for value in values:
            if isinstance(value, float) and math.isfinite(value):
                print(f"{value:g}")
            else:
                print(value)

    except AxiomError as error:
        print(f"AXIOM error: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
