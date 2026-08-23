"""JSON input parsing and result export."""

from __future__ import annotations

import csv
import json
from collections.abc import Mapping
from dataclasses import asdict
from pathlib import Path
from typing import Any, cast

from mfcblend.core import (
    Cylinder,
    FeedResult,
    FeedSystem,
    InputError,
    MFCConstraints,
    StandardConditions,
)


def _object(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise InputError(f"{label} must be a JSON object.")
    return cast(dict[str, Any], value)


def _number(value: object, label: str) -> float:
    if not isinstance(value, int | float) or isinstance(value, bool):
        raise InputError(f"{label} must be numeric.")
    return float(value)


def read_json(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    try:
        value = json.loads(source.read_text(encoding="utf-8"))
    except OSError as exc:
        raise InputError(f"Could not read {source}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise InputError(f"Invalid JSON in {source}: {exc}") from exc
    return _object(value, str(source))


def load_system(path: str | Path) -> FeedSystem:
    data = read_json(path)
    raw_conditions = data.get("standard_conditions")
    if raw_conditions is None:
        conditions = None
    else:
        conditions_data = _object(raw_conditions, "standard_conditions")
        conditions = StandardConditions(
            temperature_k=_number(conditions_data.get("temperature_k"), "temperature_k"),
            pressure_pa=_number(conditions_data.get("pressure_pa"), "pressure_pa"),
        )
    raw_cylinders = data.get("cylinders")
    if not isinstance(raw_cylinders, list):
        raise InputError("cylinders must be a JSON array.")
    cylinders: list[Cylinder] = []
    for index, raw_cylinder in enumerate(raw_cylinders):
        cylinder_data = _object(raw_cylinder, f"cylinders[{index}]")
        raw_name = cylinder_data.get("name")
        if not isinstance(raw_name, str):
            raise InputError(f"cylinders[{index}].name must be a string.")
        raw_composition = _object(
            cylinder_data.get("composition"), f"cylinders[{index}].composition"
        )
        composition = {
            str(species): _number(fraction, f"fraction {species}")
            for species, fraction in raw_composition.items()
        }
        raw_mfc = cylinder_data.get("mfc")
        if raw_mfc is None:
            mfc = None
        else:
            mfc_data = _object(raw_mfc, f"cylinders[{index}].mfc")
            turndown_raw = mfc_data.get("turndown")
            turndown = None if turndown_raw is None else _number(turndown_raw, "turndown")
            mfc = MFCConstraints(
                minimum=_number(mfc_data.get("minimum"), "minimum"),
                maximum=_number(mfc_data.get("maximum"), "maximum"),
                turndown=turndown,
            )
        cylinders.append(
            Cylinder(
                name=raw_name,
                composition=composition,
                mfc=mfc,
            )
        )
    raw_flow_unit = data.get("flow_unit")
    if not isinstance(raw_flow_unit, str):
        raise InputError("flow_unit must be a string.")
    report_data = _object(data.get("report", {}), "report")
    raw_ratios = report_data.get("ratios", [])
    if not isinstance(raw_ratios, list):
        raise InputError("report.ratios must be an array of two-species arrays.")
    ratios: list[tuple[str, str]] = []
    for index, raw_ratio in enumerate(raw_ratios):
        if (
            not isinstance(raw_ratio, list)
            or len(raw_ratio) != 2
            or not all(isinstance(value, str) for value in raw_ratio)
        ):
            raise InputError(f"report.ratios[{index}] must contain two species names.")
        ratios.append((raw_ratio[0], raw_ratio[1]))
    raw_diluents = report_data.get("diluents", [])
    if not isinstance(raw_diluents, list) or not all(
        isinstance(value, str) for value in raw_diluents
    ):
        raise InputError("report.diluents must be an array of species names.")
    return FeedSystem(
        tuple(cylinders),
        raw_flow_unit.lower(),
        conditions,
        tuple(ratios),
        tuple(raw_diluents),
    )


def load_setpoints(path: str | Path) -> dict[str, float]:
    data = read_json(path)
    raw = data.get("setpoints", data)
    return {
        key: _number(value, f"setpoint {key}") for key, value in _object(raw, "setpoints").items()
    }


def load_target(path: str | Path) -> tuple[dict[str, float], float]:
    data = read_json(path)
    target = _object(data.get("composition"), "composition")
    composition = {key: _number(value, f"target fraction {key}") for key, value in target.items()}
    return composition, _number(data.get("total_flow"), "total_flow")


def result_dict(result: FeedResult) -> dict[str, Any]:
    data = asdict(result)
    data["status"] = result.status.value
    data["scientific_basis"] = {
        "composition_basis": "molar fraction",
        "mixing_model": "steady ideal linear material balance",
        "flow_reference_model": (
            "ideal gas at explicitly supplied reference T and P"
            if result.standard_conditions is not None
            else "unknown; amount-flow conversion unavailable"
        ),
        "safety_scope": "not a process safety or flammability assessment",
    }
    return data


def export_result(result: FeedResult, path: str | Path) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.suffix.lower() == ".json":
        destination.write_text(
            json.dumps(result_dict(result), indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    elif destination.suffix.lower() == ".csv":
        _export_csv(result, destination)
    else:
        raise InputError("Result output must use a .json or .csv filename.")
    return destination


def _export_csv(result: FeedResult, destination: Path) -> None:
    rows: list[Mapping[str, str | float]] = []
    for name, value in result.setpoints.items():
        rows.append({"section": "setpoint", "name": name, "value": value, "unit": result.flow_unit})
    for species, value in result.composition.items():
        rows.append({"section": "composition", "name": species, "value": value, "unit": "mol/mol"})
    rows.append(
        {
            "section": "summary",
            "name": "total_flow",
            "value": result.total_flow,
            "unit": result.flow_unit,
        }
    )
    for name, ratio_value in result.ratios.items():
        rows.append(
            {
                "section": "ratio",
                "name": name,
                "value": "undefined" if ratio_value is None else ratio_value,
                "unit": "mol/mol",
            }
        )
    if result.diluent_fraction is not None:
        rows.append(
            {
                "section": "summary",
                "name": "diluent_fraction",
                "value": result.diluent_fraction,
                "unit": "mol/mol",
            }
        )
    rows.append({"section": "summary", "name": "status", "value": result.status.value, "unit": ""})
    with destination.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["section", "name", "value", "unit"])
        writer.writeheader()
        writer.writerows(rows)
