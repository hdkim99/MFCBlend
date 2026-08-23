"""Explicit ideal-gas conversions for standardized volumetric flows."""

from __future__ import annotations

from .models import InputError, StandardConditions

MOLAR_GAS_CONSTANT = 8.314_462_618_153_24  # J mol-1 K-1, exact in the revised SI


def _cubic_metres_per_second(value: float, unit: str) -> float:
    if value < 0:
        raise InputError("Flow cannot be negative.")
    if unit in {"sccm", "nml/min"}:
        return value * 1e-6 / 60.0
    if unit == "slm":
        return value * 1e-3 / 60.0
    raise InputError("flow unit must be one of: sccm, slm, nml/min.")


def molar_flow(value: float, unit: str, conditions: StandardConditions) -> float:
    """Return mol/s using ``n_dot = P_ref Q_ref / (R T_ref)`` (ideal gas)."""

    return (
        conditions.pressure_pa
        * _cubic_metres_per_second(value, unit)
        / (MOLAR_GAS_CONSTANT * conditions.temperature_k)
    )


def convert_reference_flow(
    value: float,
    unit: str,
    source: StandardConditions,
    destination: StandardConditions,
) -> float:
    """Convert a standardized flow between explicit ideal-gas reference conditions."""

    # Unit scale is intentionally unchanged; only the reference state changes.
    if unit not in {"sccm", "slm", "nml/min"}:
        raise InputError("flow unit must be one of: sccm, slm, nml/min.")
    if value < 0:
        raise InputError("Flow cannot be negative.")
    return (
        value
        * (source.pressure_pa / source.temperature_k)
        * (destination.temperature_k / destination.pressure_pa)
    )
