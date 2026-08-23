"""Real Tk widget lifecycle and export smoke, run under Aqua or Xvfb."""

from __future__ import annotations

import argparse
from pathlib import Path
from tkinter import Tk

from mfcblend.gui.app import MFCBlendApp


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("system", type=Path)
    parser.add_argument("values", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--mode", choices=("forward", "inverse"), default="inverse")
    args = parser.parse_args()
    root = Tk()
    root.withdraw()
    try:
        app = MFCBlendApp(root)
        result = app.run_from_paths(args.system, args.values, args.mode, args.output)
        assert result.status.value == "exact"
        assert args.output.is_file() and args.output.stat().st_size > 0
    finally:
        root.update_idletasks()
        root.destroy()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
