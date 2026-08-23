"""Headless command-line adapter."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from mfcblend import __version__
from mfcblend.application import RunRequest, execute
from mfcblend.core import InputError
from mfcblend.io import export_result, load_system, result_dict


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mfcblend",
        description="Plan catalytic-reactor gas feeds from cylinders and constrained MFCs.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate a feed-system JSON file")
    validate.add_argument("system", type=Path)

    for mode in ("forward", "inverse"):
        command = subparsers.add_parser(mode, help=f"run a {mode} gas-feed calculation")
        command.add_argument(
            "system",
            type=Path,
            help="cylinders plus reported MFC limits/reference conditions (null if unknown)",
        )
        command.add_argument(
            "values", type=Path, help="setpoints JSON (forward) or target JSON (inverse)"
        )
        command.add_argument("--output", type=Path, help="write a .json or .csv result")
        if mode == "inverse":
            command.add_argument(
                "--allow-approximate",
                action="store_true",
                help="return a clearly labelled approximate plan when no exact plan exists",
            )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "validate":
            system = load_system(args.system)
            print(
                json.dumps(
                    {
                        "status": "valid",
                        "cylinders": len(system.cylinders),
                        "species": system.species,
                        "flow_unit": system.flow_unit,
                    },
                    indent=2,
                )
            )
            return 0
        request = RunRequest(
            system_path=args.system,
            values_path=args.values,
            mode=args.command,
            allow_approximate=getattr(args, "allow_approximate", False),
        )
        result = execute(request)
        if args.output:
            export_result(result, args.output)
        print(json.dumps(result_dict(result), indent=2, sort_keys=True))
        return 2 if result.status.value == "infeasible" else 0
    except (InputError, OSError, ValueError) as exc:
        print(f"mfcblend: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
