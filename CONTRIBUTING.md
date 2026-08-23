# Contributing

Contributions are welcome. Do not post unpublished, export-controlled,
proprietary, or confidential experimental data in a public issue.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
ruff format --check .
ruff check .
mypy src
pytest
python -m build
twine check dist/*
```

A scientific-core change must state the equation or definition, units and basis,
assumptions, validity boundary, authoritative reference or derivation, numerical
validation, and regression test. Do not add an empirical threshold, coefficient,
uncertainty, or confidence interval without a verifiable source and applicability
range.

A GUI change must additionally document platform support, dependency/backend
impact, macOS smoke evidence, and CLI/core import isolation. Do not move formulas
into the GUI or initialize Tk/Matplotlib from a scientific-core import.

External fork pull requests do not execute on the persistent DGX runner. A
maintainer must review untrusted code before trusted-hardware execution.
