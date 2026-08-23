"""Forward and constrained inverse linear gas-mixing calculations."""

from __future__ import annotations

from collections.abc import Mapping
from itertools import combinations
from math import isfinite

import numpy as np
from scipy.optimize import lsq_linear

from .models import FeedResult, FeedSystem, InputError, SolutionStatus


def _ordered_setpoints(system: FeedSystem, setpoints: Mapping[str, float]) -> np.ndarray:
    unknown = set(setpoints) - {cylinder.name for cylinder in system.cylinders}
    if unknown:
        raise InputError(f"Unknown cylinder setpoints: {', '.join(sorted(unknown))}.")
    ordered: list[float] = []
    for cylinder in system.cylinders:
        value = float(setpoints.get(cylinder.name, 0.0))
        if not isfinite(value):
            raise InputError(f"Setpoint for {cylinder.name!r} must be finite.")
        if not cylinder.mfc.accepts(value):
            raise InputError(
                f"Setpoint {value:g} for {cylinder.name!r} is neither off nor within "
                f"[{cylinder.mfc.effective_minimum:g}, {cylinder.mfc.maximum:g}] "
                f"{system.flow_unit}."
            )
        ordered.append(0.0 if abs(value) <= 1e-12 else value)
    return np.asarray(ordered, dtype=float)


def _forward_from_vector(system: FeedSystem, flows: np.ndarray) -> FeedResult:
    total = float(np.sum(flows))
    if total <= 0:
        raise InputError("Total flow must be greater than zero.")
    component_flows = {
        species: float(
            sum(
                flow * cylinder.composition.get(species, 0.0)
                for flow, cylinder in zip(flows, system.cylinders, strict=True)
            )
        )
        for species in system.species
    }
    composition = {
        species: component_flow / total for species, component_flow in component_flows.items()
    }
    ratios = {
        f"{numerator}/{denominator}": (
            None
            if composition[denominator] == 0
            else composition[numerator] / composition[denominator]
        )
        for numerator, denominator in system.reported_ratios
    }
    diluent_fraction = (
        sum(composition[species] for species in system.diluents) if system.diluents else None
    )
    return FeedResult(
        status=SolutionStatus.EXACT,
        setpoints={
            cylinder.name: float(flow)
            for cylinder, flow in zip(system.cylinders, flows, strict=True)
        },
        total_flow=total,
        composition=composition,
        component_flows=component_flows,
        flow_unit=system.flow_unit,
        standard_conditions=system.standard_conditions,
        ratios=ratios,
        diluent_fraction=diluent_fraction,
        messages=(
            "Composition is a molar-fraction result from ideal mixing of the stated "
            "cylinder compositions.",
            "This plan does not assess mixture flammability, compatibility, or process safety.",
        ),
    )


def forward_mix(system: FeedSystem, setpoints: Mapping[str, float]) -> FeedResult:
    """Calculate the mixed feed from user-supplied MFC setpoints."""

    return _forward_from_vector(system, _ordered_setpoints(system, setpoints))


def _validate_target(
    system: FeedSystem, target_composition: Mapping[str, float], total_flow: float
) -> dict[str, float]:
    if not isfinite(total_flow) or total_flow <= 0:
        raise InputError("Target total flow must be finite and greater than zero.")
    if not target_composition:
        raise InputError("At least one target species fraction is required.")
    target: dict[str, float] = {}
    for species, value in target_composition.items():
        if species not in system.species:
            raise InputError(f"Target species {species!r} is absent from every cylinder.")
        fraction = float(value)
        if not isfinite(fraction) or fraction < 0 or fraction > 1:
            raise InputError(f"Target fraction for {species!r} must be finite and within [0, 1].")
        target[species] = fraction
    closure = sum(target.values())
    if closure > 1 + 1e-9:
        raise InputError(f"Specified target fractions sum to {closure:.12g}, which exceeds 1.")
    return target


def _active_subsets(count: int) -> list[tuple[int, ...]]:
    if count > 16:
        raise InputError(
            "Inverse planning currently supports at most 16 MFCs because off/on limits "
            "are enumerated exactly."
        )
    return [subset for size in range(1, count + 1) for subset in combinations(range(count), size)]


def inverse_mix(
    system: FeedSystem,
    target_composition: Mapping[str, float],
    total_flow: float,
    *,
    allow_approximate: bool = False,
    composition_tolerance: float = 1e-7,
    total_flow_tolerance: float = 1e-7,
) -> FeedResult:
    """Solve constrained MFC setpoints for a requested final feed.

    The model is the linear material balance ``A q = b``. Each MFC may be off,
    or it must lie inside its effective operating range. Those disjoint bounds
    are handled by enumerating active MFC subsets and solving each bounded
    linear least-squares problem. An approximate solution is returned only when
    ``allow_approximate`` is true.
    """

    target = _validate_target(system, target_composition, total_flow)
    if composition_tolerance <= 0 or total_flow_tolerance <= 0:
        raise InputError("Inverse-solver tolerances must be greater than zero.")
    target_species = tuple(target)
    best: tuple[float, np.ndarray, FeedResult, float, float] | None = None

    for active in _active_subsets(len(system.cylinders)):
        component_matrix = np.asarray(
            [
                [system.cylinders[index].composition.get(species, 0.0) for index in active]
                for species in target_species
            ],
            dtype=float,
        )
        # Normalize all material-balance rows by target total flow. This makes
        # component and total-flow residuals dimensionless and comparable.
        matrix = np.vstack((component_matrix, np.ones(len(active), dtype=float))) / total_flow
        rhs = np.asarray([*target.values(), 1.0], dtype=float)
        lower = np.asarray(
            [system.cylinders[index].mfc.effective_minimum for index in active], dtype=float
        )
        upper = np.asarray([system.cylinders[index].mfc.maximum for index in active], dtype=float)
        fixed = np.isclose(lower, upper, rtol=1e-12, atol=1e-12)
        active_solution = np.empty(len(active), dtype=float)
        active_solution[fixed] = (lower[fixed] + upper[fixed]) / 2
        remaining_rhs = rhs - matrix[:, fixed] @ active_solution[fixed]
        if np.any(~fixed):
            solved = lsq_linear(
                matrix[:, ~fixed],
                remaining_rhs,
                bounds=(lower[~fixed], upper[~fixed]),
                lsmr_tol="auto",
            )
            active_solution[~fixed] = solved.x
        flows = np.zeros(len(system.cylinders), dtype=float)
        flows[list(active)] = active_solution
        try:
            forward = _forward_from_vector(system, flows)
        except InputError:
            continue
        composition_error = max(
            abs(forward.composition.get(species, 0.0) - fraction)
            for species, fraction in target.items()
        )
        flow_error = abs(forward.total_flow - total_flow)
        residual = float(np.linalg.norm(matrix @ active_solution - rhs))
        if best is None or residual < best[0]:
            best = (residual, flows, forward, composition_error, flow_error)

    if best is None:
        return FeedResult(
            status=SolutionStatus.INFEASIBLE,
            setpoints={},
            total_flow=0.0,
            composition={},
            component_flows={},
            flow_unit=system.flow_unit,
            standard_conditions=system.standard_conditions,
            target_composition=target,
            target_total_flow=total_flow,
            messages=(
                "Target composition is infeasible with the available cylinders and MFC "
                "operating ranges.",
                "No setpoints are returned as a successful plan.",
            ),
        )

    _, flows, forward, composition_error, flow_error = best
    is_exact = (
        composition_error <= composition_tolerance
        and flow_error <= total_flow_tolerance * max(1.0, total_flow)
    )
    if not is_exact and not allow_approximate:
        return FeedResult(
            status=SolutionStatus.INFEASIBLE,
            setpoints={},
            total_flow=forward.total_flow,
            composition=forward.composition,
            component_flows=forward.component_flows,
            flow_unit=system.flow_unit,
            standard_conditions=system.standard_conditions,
            target_composition=target,
            target_total_flow=total_flow,
            maximum_composition_error=composition_error,
            total_flow_error=flow_error,
            ratios=forward.ratios,
            diluent_fraction=forward.diluent_fraction,
            messages=(
                "Target composition is infeasible within the requested tolerances and MFC "
                "operating ranges.",
                "The achieved composition is diagnostic only; no setpoints are returned "
                "as a successful plan.",
            ),
        )

    status = SolutionStatus.EXACT if is_exact else SolutionStatus.APPROXIMATE
    status_message = (
        "An exact constrained material-balance solution was found."
        if is_exact
        else "Only an approximate constrained solution was found; review the reported residuals."
    )
    return FeedResult(
        status=status,
        setpoints={
            cylinder.name: float(flow)
            for cylinder, flow in zip(system.cylinders, flows, strict=True)
        },
        total_flow=forward.total_flow,
        composition=forward.composition,
        component_flows=forward.component_flows,
        flow_unit=system.flow_unit,
        standard_conditions=system.standard_conditions,
        target_composition=target,
        target_total_flow=total_flow,
        maximum_composition_error=composition_error,
        total_flow_error=flow_error,
        ratios=forward.ratios,
        diluent_fraction=forward.diluent_fraction,
        messages=(
            status_message,
            "The solve uses ideal linear mixing on a molar-flow basis.",
            "This plan does not assess mixture flammability, compatibility, or process safety.",
        ),
    )
