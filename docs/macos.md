# macOS GUI support and verification

MFCBlend uses the standard-library Tkinter/ttk adapter. It does not depend on
PyQt, PySide, Qt, or PyQtGraph.

## Support target

- macOS 13 or newer;
- Python 3.10–3.14 from Python.org or Homebrew when that distribution includes a
  working Tkinter;
- Apple Silicon and Intel source/wheel installation targets.

GitHub `macos-15` (Apple Silicon) runs Python 3.10 and 3.14 checks;
`macos-15-intel` runs Python 3.13 checks. GitHub documents those labels as arm64
and Intel respectively in its
[hosted-runners reference](https://docs.github.com/en/actions/reference/runners/github-hosted-runners).
Local verification records the actual Mac architecture and Python/Tk versions
in the release checklist. A platform/architecture combination not shown by a
passing job or release checklist is **not verified**.

## Clean smoke test

```bash
python3 -m venv /tmp/mfcblend-macos-smoke
/tmp/mfcblend-macos-smoke/bin/python -m pip install ".[gui]"
/tmp/mfcblend-macos-smoke/bin/python -c "import tkinter; print(tkinter.TkVersion)"
/tmp/mfcblend-macos-smoke/bin/python -m mfcblend.gui --smoke-test \
  --system examples/co2_hydrogen_system.json \
  --values examples/target_5co2_20h2.json \
  --mode inverse \
  --output /tmp/mfcblend-gui-result.json
```

Normal output is a nonempty JSON result with status `exact`, followed by a clean
process exit. The smoke path creates one `Tk()` root, runs calculation/export
through real widgets, and destroys the root.

If initialization fails, collect:

```bash
sw_vers
uname -m
python3 --version
python3 -c "import tkinter; print(tkinter.TkVersion)"
python3 -m pip freeze
python3 -m mfcblend.gui
```

The GUI error includes the Python version, operating system, optional install
command, and supported entry point. Do not install PyQt or PySide to repair a Tk
failure.

## Backend policy

- the core, application layer, I/O, and CLI import neither Tkinter nor Matplotlib;
- optional figure export selects `Agg` only inside the plotting function;
- the Tk GUI does not import `matplotlib.pyplot`;
- no environment variable is used to hide display or Qt plugin failures.
