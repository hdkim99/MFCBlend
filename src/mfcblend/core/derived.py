"""Derived reactor-feed quantities with explicit bases."""

from __future__ import annotations

from collections.abc import Mapping

from .models import FeedResult, InputError
from .standard import molar_flow


def total_molar_flow(result: FeedResult) -> float:
    """Return ideal-gas molar flow in mol/s at the stated reference conditions."""

    return molar_flow(result.total_flow, result.flow_unit, result.standard_conditions)


def partial_pressures(
    composition: Mapping[str, float], total_pressure_pa: float
) -> dict[str, float]:
    """Return ideal-mixture partial pressures in Pa using ``p_i = y_i P``."""

    if total_pressure_pa <= 0:
        raise InputError("Total pressure must be greater than zero Pa absolute.")
    return {species: fraction * total_pressure_pa for species, fraction in composition.items()}


def ghsv(result: FeedResult, catalyst_bed_volume_ml: float) -> float:
    """Return GHSV in h^-1 from reference volumetric flow / catalyst-bed volume.

    This uses the same standard/reference conditions attached to ``result``.
    It does not convert the feed to reactor-temperature actual volume.
    """

    if catalyst_bed_volume_ml <= 0:
        raise InputError("Catalyst-bed volume must be greater than zero mL.")
    if result.flow_unit in {"sccm", "nml/min"}:
        flow_ml_min = result.total_flow
    elif result.flow_unit == "slm":
        flow_ml_min = result.total_flow * 1000.0
    else:  # defensive: FeedSystem already validates this
        raise InputError(f"Unsupported flow unit {result.flow_unit!r}.")
    return flow_ml_min * 60.0 / catalyst_bed_volume_ml
