"""Tkinter/ttk desktop adapter.

The GUI contains no scientific equations; it calls the same application
service as the CLI.
"""

from __future__ import annotations

import platform
import sys
from pathlib import Path
from tkinter import BOTH, END, LEFT, RIGHT, StringVar, Tk, X, filedialog, messagebox, ttk

from mfcblend.application import RunRequest, execute
from mfcblend.core import FeedResult, InputError
from mfcblend.io import export_result


class MFCBlendApp(ttk.Frame):
    """Main desktop workflow widget."""

    def __init__(self, master: Tk) -> None:
        super().__init__(master, padding=12)
        self.root = master
        self.root.title("MFCBlend")
        self.root.minsize(760, 500)
        self.pack(fill=BOTH, expand=True)
        self.system_path = StringVar()
        self.values_path = StringVar()
        self.mode = StringVar(value="inverse")
        self.status = StringVar(value="Load a feed system and values file.")
        self._result: FeedResult | None = None
        self._build()

    def _build(self) -> None:
        title = ttk.Label(
            self, text="Catalytic reactor gas-feed planner", font=("TkDefaultFont", 16)
        )
        title.pack(anchor="w", pady=(0, 10))
        note = ttk.Label(
            self,
            text=(
                "Ideal linear mixing; unreported MFC limits and reference conditions stay unknown. "
                "Not a process-safety assessment."
            ),
            wraplength=720,
        )
        note.pack(anchor="w", pady=(0, 10))

        controls = ttk.Frame(self)
        controls.pack(fill=X)
        ttk.Label(controls, text="Mode").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=4)
        ttk.Combobox(
            controls,
            textvariable=self.mode,
            values=("inverse", "forward"),
            state="readonly",
            width=12,
        ).grid(row=0, column=1, sticky="w", pady=4)
        self._path_row(controls, 1, "System JSON", self.system_path)
        self._path_row(controls, 2, "Target/setpoints JSON", self.values_path)
        controls.columnconfigure(1, weight=1)

        actions = ttk.Frame(self)
        actions.pack(fill=X, pady=10)
        ttk.Button(actions, text="Calculate", command=self.calculate).pack(side=LEFT)
        ttk.Button(actions, text="Export…", command=self.export).pack(side=LEFT, padx=8)
        ttk.Label(actions, textvariable=self.status).pack(side=RIGHT)

        self.results = ttk.Treeview(self, columns=("name", "value", "unit"), show="headings")
        self.results.heading("name", text="Quantity")
        self.results.heading("value", text="Value")
        self.results.heading("unit", text="Unit / basis")
        self.results.column("name", width=260)
        self.results.column("value", width=180, anchor="e")
        self.results.column("unit", width=180)
        self.results.pack(fill=BOTH, expand=True)

    def _path_row(self, parent: ttk.Frame, row: int, label: str, variable: StringVar) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=(0, 8), pady=4)
        ttk.Entry(parent, textvariable=variable).grid(row=row, column=1, sticky="ew", pady=4)
        ttk.Button(parent, text="Browse…", command=lambda: self._browse(variable)).grid(
            row=row, column=2, padx=(8, 0), pady=4
        )

    @staticmethod
    def _browse(variable: StringVar) -> None:
        selected = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*")]
        )
        if selected:
            variable.set(selected)

    def calculate(self) -> FeedResult | None:
        try:
            result = execute(
                RunRequest(
                    system_path=Path(self.system_path.get()),
                    values_path=Path(self.values_path.get()),
                    mode=self.mode.get(),
                )
            )
        except (InputError, OSError, ValueError) as exc:
            self.status.set("Calculation failed")
            messagebox.showerror("MFCBlend", str(exc), parent=self.root)
            return None
        self._result = result
        self._show_result(result)
        self.status.set(f"Result: {result.status.value}")
        return result

    def _show_result(self, result: FeedResult) -> None:
        self.results.delete(*self.results.get_children())
        self.results.insert("", END, values=("Status", result.status.value, ""))
        self.results.insert(
            "", END, values=("Total flow", f"{result.total_flow:.8g}", result.flow_unit)
        )
        for name, value in result.setpoints.items():
            self.results.insert("", END, values=(f"MFC {name}", f"{value:.8g}", result.flow_unit))
        for species, value in result.composition.items():
            self.results.insert("", END, values=(f"y({species})", f"{value:.8g}", "mol/mol"))
        for name, ratio_value in result.ratios.items():
            shown = "undefined (zero denominator)" if ratio_value is None else f"{ratio_value:.8g}"
            self.results.insert("", END, values=(name, shown, "molar ratio"))
        if result.diluent_fraction is not None:
            self.results.insert(
                "",
                END,
                values=("Diluent fraction", f"{result.diluent_fraction:.8g}", "mol/mol"),
            )

    def export(self, destination: str | Path | None = None) -> Path | None:
        if self._result is None:
            messagebox.showinfo(
                "MFCBlend", "Calculate a result before exporting.", parent=self.root
            )
            return None
        target = destination
        if target is None:
            selected = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON result", "*.json"), ("CSV result", "*.csv")],
            )
            if not selected:
                return None
            target = selected
        exported = export_result(self._result, target)
        self.status.set(f"Exported {exported.name}")
        return exported

    def run_from_paths(
        self,
        system_path: str | Path,
        values_path: str | Path,
        mode: str,
        destination: str | Path,
    ) -> FeedResult:
        """Drive the real widget workflow for smoke tests."""

        self.system_path.set(str(system_path))
        self.values_path.set(str(values_path))
        self.mode.set(mode)
        result = self.calculate()
        if result is None:
            raise RuntimeError("GUI workflow calculation failed.")
        if self.export(destination) is None:
            raise RuntimeError("GUI workflow export failed.")
        self.root.update_idletasks()
        return result


def dependency_error(exc: BaseException) -> str:
    return (
        "MFCBlend GUI could not initialize Tkinter.\n"
        f"Reason: {exc}\n"
        f"Python: {platform.python_version()}\n"
        f"Operating system: {platform.platform()}\n"
        "The scientific core and CLI do not require a GUI backend.\n"
        'Install with: pip install "mfcblend[gui]"\n'
        "Then run: python -m mfcblend.gui"
    )


def create_root() -> Tk:
    try:
        return Tk()
    except Exception as exc:
        raise RuntimeError(dependency_error(exc)) from exc


def main() -> int:
    try:
        root = create_root()
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        return 2
    MFCBlendApp(root)
    root.mainloop()
    return 0
