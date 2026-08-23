from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from mfcblend.application import RunRequest, execute_and_export
from mfcblend.core import SolutionStatus
from mfcblend.io import load_system

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.integration
def test_application_and_json_export(tmp_path: Path) -> None:
    output = tmp_path / "result.json"
    result = execute_and_export(
        RunRequest(
            ROOT / "examples/co2_hydrogen_system.json",
            ROOT / "examples/target_5co2_20h2.json",
            "inverse",
        ),
        output,
    )
    assert result.status is SolutionStatus.EXACT
    exported = json.loads(output.read_text(encoding="utf-8"))
    assert exported["status"] == "exact"
    assert exported["scientific_basis"]["composition_basis"] == "molar fraction"
    assert exported["ratios"]["H2/CO2"] == pytest.approx(4)
    assert exported["diluent_fraction"] == pytest.approx(0.75)


@pytest.mark.integration
def test_csv_export(tmp_path: Path) -> None:
    output = tmp_path / "result.csv"
    execute_and_export(
        RunRequest(
            ROOT / "examples/co2_hydrogen_system.json",
            ROOT / "examples/setpoints_5co2_20h2.json",
            "forward",
        ),
        output,
    )
    text = output.read_text(encoding="utf-8")
    assert "setpoint,CO2_mix,100.0,sccm" in text
    assert "composition,CO2,0.05,mol/mol" in text


@pytest.mark.integration
def test_cli_inverse_and_infeasible_exit_status(tmp_path: Path) -> None:
    environment = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    exact = subprocess.run(
        [
            sys.executable,
            "-m",
            "mfcblend.cli",
            "inverse",
            "examples/co2_hydrogen_system.json",
            "examples/target_5co2_20h2.json",
            "--output",
            str(tmp_path / "exact.json"),
        ],
        cwd=ROOT,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    assert exact.returncode == 0, exact.stderr
    assert '"status": "exact"' in exact.stdout
    infeasible = subprocess.run(
        [
            sys.executable,
            "-m",
            "mfcblend.cli",
            "inverse",
            "examples/co2_hydrogen_system.json",
            "examples/infeasible_target.json",
        ],
        cwd=ROOT,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    assert infeasible.returncode == 2
    assert '"status": "infeasible"' in infeasible.stdout


def test_cli_and_core_import_do_not_load_gui_or_plotting() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys, mfcblend, mfcblend.cli; "
                "assert 'tkinter' not in sys.modules; "
                "assert 'matplotlib.pyplot' not in sys.modules"
            ),
        ],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr


def test_config_records_explicit_reference_conditions() -> None:
    system = load_system(ROOT / "examples/co2_hydrogen_system.json")
    assert system.standard_conditions.temperature_k == 273.15
    assert system.standard_conditions.pressure_pa == 101325
