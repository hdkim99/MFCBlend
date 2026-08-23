"""Validated domain models for gas-feed planning.

All compositions are molar fractions. Flow numbers are equivalent volumetric
flows at one explicitly supplied reference temperature and pressure.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from math import isfinite


class InputError(ValueError):
    """Raised when an input is mathematically or physically invalid."""


def _require_finite(name: str, value: float) -> None:
    if not isfinite(value):
        raise InputError(f"{name} must be finite; received {value!r}.")


@dataclass(frozen=True)
class StandardConditions:
    """Reference conditions attached to an equivalent volumetric gas flow."""

    temperature_k: float
    pressure_pa: float

    def __post_init__(self) -> None:
        _require_finite("reference temperature", self.temperature_k)
        _require_finite("reference pressure", self.pressure_pa)
        if self.temperature_k <= 0:
            raise InputError("Reference temperature must be greater than 0 K.")
        if self.pressure_pa <= 0:
            raise InputError("Reference pressure must be greater than 0 Pa absolute.")


@dataclass(frozen=True)
class MFCConstraints:
    """Setpoint limits for one MFC, in the plan's common flow unit.

    An MFC may be off (zero) or operate from ``effective_minimum`` through
    ``maximum``. ``turndown`` is full-scale flow divided by minimum controllable
    flow; the tool does not infer a vendor-specific turndown when it is omitted.
    """

    minimum: float
    maximum: float
    turndown: float | None = None

    def __post_init__(self) -> None:
        _require_finite("MFC minimum", self.minimum)
        _require_finite("MFC maximum", self.maximum)
        if self.minimum < 0:
            raise InputError("MFC minimum cannot be negative.")
        if self.maximum <= 0:
            raise InputError("MFC maximum must be greater than zero.")
        if self.minimum > self.maximum:
            raise InputError("MFC minimum cannot exceed MFC maximum.")
        if self.turndown is not None:
            _require_finite("MFC turndown", self.turndown)
            if self.turndown < 1:
                raise InputError("MFC turndown must be at least 1 (full scale / minimum).")

    @property
    def effective_minimum(self) -> float:
        turndown_minimum = 0.0 if self.turndown is None else self.maximum / self.turndown
        return max(self.minimum, turndown_minimum)

    def accepts(self, flow: float, *, atol: float = 1e-12) -> bool:
        _require_finite("MFC setpoint", flow)
        if abs(flow) <= atol:
            return True
        return self.effective_minimum - atol <= flow <= self.maximum + atol


@dataclass(frozen=True)
class Cylinder:
    """A cylinder composition and the constraints of its connected MFC."""

    name: str
    composition: Mapping[str, float]
    mfc: MFCConstraints

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InputError("Cylinder name cannot be empty.")
        if not self.composition:
            raise InputError(f"Cylinder {self.name!r} must contain at least one species.")
        normalized: dict[str, float] = {}
        for species, fraction in self.composition.items():
            if not species.strip():
                raise InputError(f"Cylinder {self.name!r} contains an empty species name.")
            _require_finite(f"fraction of {species} in {self.name}", fraction)
            if fraction < 0 or fraction > 1:
                raise InputError(f"Fraction of {species!r} in {self.name!r} must be within [0, 1].")
            normalized[species.strip()] = float(fraction)
        closure = sum(normalized.values())
        if abs(closure - 1.0) > 1e-9:
            raise InputError(f"Cylinder {self.name!r} composition sums to {closure:.12g}, not 1.")
        object.__setattr__(self, "composition", normalized)


@dataclass(frozen=True)
class FeedSystem:
    """Cylinders sharing one flow unit and reference condition convention."""

    cylinders: tuple[Cylinder, ...]
    flow_unit: str
    standard_conditions: StandardConditions
    reported_ratios: tuple[tuple[str, str], ...] = ()
    diluents: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.cylinders:
            raise InputError("At least one cylinder is required.")
        names = [cylinder.name for cylinder in self.cylinders]
        if len(set(names)) != len(names):
            raise InputError("Cylinder names must be unique.")
        if self.flow_unit not in {"sccm", "slm", "nml/min"}:
            raise InputError("flow_unit must be one of: sccm, slm, nml/min.")
        known_species = set(self.species)
        for numerator, denominator in self.reported_ratios:
            if numerator not in known_species or denominator not in known_species:
                raise InputError(
                    f"Reported ratio {numerator}/{denominator} refers to an unknown species."
                )
        unknown_diluents = set(self.diluents) - known_species
        if unknown_diluents:
            raise InputError(
                f"Diluents are absent from every cylinder: {', '.join(sorted(unknown_diluents))}."
            )

    @property
    def species(self) -> tuple[str, ...]:
        return tuple(
            sorted({species for cylinder in self.cylinders for species in cylinder.composition})
        )

    def cylinder(self, name: str) -> Cylinder:
        for cylinder in self.cylinders:
            if cylinder.name == name:
                return cylinder
        raise InputError(f"Unknown cylinder {name!r}.")


class SolutionStatus(str, Enum):
    EXACT = "exact"
    APPROXIMATE = "approximate"
    INFEASIBLE = "infeasible"


@dataclass(frozen=True)
class FeedResult:
    """Common forward/inverse feed result."""

    status: SolutionStatus
    setpoints: Mapping[str, float]
    total_flow: float
    composition: Mapping[str, float]
    component_flows: Mapping[str, float]
    flow_unit: str
    standard_conditions: StandardConditions
    messages: tuple[str, ...] = field(default_factory=tuple)
    target_composition: Mapping[str, float] | None = None
    target_total_flow: float | None = None
    maximum_composition_error: float | None = None
    total_flow_error: float | None = None
    ratios: Mapping[str, float | None] = field(default_factory=dict)
    diluent_fraction: float | None = None
