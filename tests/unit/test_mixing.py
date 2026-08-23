from __future__ import annotations

import pytest

from mfcblend.core import (
    Cylinder,
    FeedSystem,
    InputError,
    MFCConstraints,
    SolutionStatus,
    StandardConditions,
    forward_mix,
    inverse_mix,
)


def system() -> FeedSystem:
    return FeedSystem(
        cylinders=(
            Cylinder("A", {"CO2": 0.10, "N2": 0.90}, MFCConstraints(2, 200, 100)),
            Cylinder("B", {"H2": 0.50, "N2": 0.50}, MFCConstraints(2, 200, 100)),
            Cylinder("C", {"N2": 1.0}, MFCConstraints(1, 500, 200)),
        ),
        flow_unit="sccm",
        standard_conditions=StandardConditions(273.15, 101325),
        reported_ratios=(("H2", "CO2"),),
        diluents=("N2",),
    )


@pytest.mark.scientific
def test_forward_hand_calculation_and_composition_closure() -> None:
    result = forward_mix(system(), {"A": 100, "B": 80, "C": 20})
    assert result.total_flow == pytest.approx(200)
    assert result.composition == pytest.approx({"CO2": 0.05, "H2": 0.20, "N2": 0.75})
    assert sum(result.composition.values()) == pytest.approx(1)
    assert result.ratios == pytest.approx({"H2/CO2": 4.0})
    assert result.diluent_fraction == pytest.approx(0.75)


@pytest.mark.scientific
def test_exact_inverse_recovers_unique_premix_solution() -> None:
    result = inverse_mix(system(), {"CO2": 0.05, "H2": 0.20}, 200)
    assert result.status is SolutionStatus.EXACT
    assert result.setpoints == pytest.approx({"A": 100, "B": 80, "C": 20})
    assert result.composition["N2"] == pytest.approx(0.75)
    assert result.maximum_composition_error is not None
    assert result.maximum_composition_error < 1e-9


def test_mfc_may_be_off_but_not_below_effective_minimum() -> None:
    assert forward_mix(system(), {"A": 0, "B": 80, "C": 120}).total_flow == 200
    with pytest.raises(InputError, match="neither off nor within"):
        forward_mix(system(), {"A": 1, "B": 80, "C": 119})


def test_infeasible_target_does_not_return_setpoints_as_success() -> None:
    result = inverse_mix(system(), {"CO2": 0.50, "H2": 0.20}, 200)
    assert result.status is SolutionStatus.INFEASIBLE
    assert result.setpoints == {}
    assert "diagnostic only" in " ".join(result.messages)


def test_approximate_solution_requires_explicit_opt_in() -> None:
    result = inverse_mix(system(), {"CO2": 0.50, "H2": 0.20}, 200, allow_approximate=True)
    assert result.status is SolutionStatus.APPROXIMATE
    assert result.setpoints
    assert result.maximum_composition_error is not None
    assert result.maximum_composition_error > 0


def test_unknown_or_nonclosing_input_is_rejected() -> None:
    with pytest.raises(InputError, match="sums to"):
        Cylinder("bad", {"N2": 0.8}, MFCConstraints(0, 10))
    with pytest.raises(InputError, match="absent"):
        inverse_mix(system(), {"CH4": 0.1}, 100)
    with pytest.raises(InputError, match="exceeds 1"):
        inverse_mix(system(), {"CO2": 0.6, "H2": 0.6}, 100)


def test_overdetermined_exact_solution() -> None:
    pure = FeedSystem(
        (
            Cylinder("H2", {"H2": 1.0}, MFCConstraints(0, 100)),
            Cylinder("N2", {"N2": 1.0}, MFCConstraints(0, 100)),
        ),
        "sccm",
        StandardConditions(298.15, 101325),
    )
    result = inverse_mix(pure, {"H2": 0.25, "N2": 0.75}, 80)
    assert result.status is SolutionStatus.EXACT
    assert result.setpoints == pytest.approx({"H2": 20, "N2": 60})


def test_inverse_solver_limit_is_explicit() -> None:
    cylinders = tuple(
        Cylinder(f"N2-{index}", {"N2": 1.0}, MFCConstraints(0, 10)) for index in range(17)
    )
    large = FeedSystem(cylinders, "sccm", StandardConditions(273.15, 101325))
    with pytest.raises(InputError, match="at most 16"):
        inverse_mix(large, {"N2": 1.0}, 10)


def test_fixed_full_scale_mfc_is_supported() -> None:
    fixed = FeedSystem(
        (Cylinder("fixed", {"N2": 1.0}, MFCConstraints(10, 10, 1)),),
        "sccm",
        StandardConditions(273.15, 101325),
    )
    result = inverse_mix(fixed, {"N2": 1.0}, 10)
    assert result.status is SolutionStatus.EXACT
    assert result.setpoints == pytest.approx({"fixed": 10})
