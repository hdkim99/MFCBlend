"""GUI namespace. Importing this module does not create a Tk root."""

from __future__ import annotations

import platform
import sys


def missing_dependency_message(exc: BaseException) -> str:
    return (
        "MFCBlend GUI dependencies are unavailable.\n"
        f"Reason: {exc}\n"
        f"Python: {platform.python_version()}\n"
        f"Operating system: {platform.platform()}\n"
        "Use a Python distribution that includes Tkinter, then install optional support with:\n"
        'pip install "mfcblend[gui]"\n'
        "Run the GUI with: python -m mfcblend.gui"
    )


def main() -> int:
    try:
        from .app import main as app_main
    except ImportError as exc:
        print(missing_dependency_message(exc), file=sys.stderr)
        return 2

    return app_main()


__all__ = ["main", "missing_dependency_message"]
