from __future__ import annotations

import argparse
from pathlib import Path


def _main() -> int:
    parser = argparse.ArgumentParser(description="Launch the MFCBlend Tkinter GUI.")
    parser.add_argument("--smoke-test", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--system", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--values", type=Path, help=argparse.SUPPRESS)
    parser.add_argument(
        "--mode", choices=("forward", "inverse"), default="inverse", help=argparse.SUPPRESS
    )
    parser.add_argument("--output", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if not args.smoke_test:
        from . import main

        return main()

    if not args.system or not args.values or not args.output:
        parser.error("--smoke-test requires --system, --values, and --output")
    try:
        from .app import MFCBlendApp, create_root
    except ImportError as exc:
        import sys

        from . import missing_dependency_message

        print(missing_dependency_message(exc), file=sys.stderr)
        return 2

    root = create_root()
    root.withdraw()
    try:
        app = MFCBlendApp(root)
        app.run_from_paths(args.system, args.values, args.mode, args.output)
    finally:
        root.update_idletasks()
        root.destroy()
    return 0


raise SystemExit(_main())
