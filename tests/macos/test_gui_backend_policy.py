from __future__ import annotations

import ast
from pathlib import Path


def test_scientific_core_has_no_gui_or_matplotlib_imports() -> None:
    root = Path(__file__).resolve().parents[2] / "src/mfcblend/core"
    forbidden = {"tkinter", "PyQt5", "PyQt6", "PySide2", "PySide6", "matplotlib"}
    for path in root.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imports |= {
            (node.module or "").split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        }
        assert imports.isdisjoint(forbidden), (path, imports & forbidden)
