from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from mfcblend.core import (
    InputError,
    SolutionStatus,
    forward_mix,
    ghsv,
    inverse_mix,
    total_molar_flow,
)
from mfcblend.io import load_setpoints, load_system

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "examples/public"

FIXTURE_SHA256 = {
    "MFC-PUB-001-system.json": "75c25661eee1845dd40009e524f7da26a77a443b007b9f7d9d41763dc838ba80",
    "MFC-PUB-001-setpoints.json": (
        "f4dcfd1f6e505d61c170cc41f4f2a219b74ae1fb5ce04b5f8d3b54400c6e4ed0"
    ),
    "MFC-PUB-002-system.json": "0b1fdba131e87824f110e2300c0c2b124eb6a3ba542867346191c339b544e693",
    "MFC-PUB-002-setpoints.json": (
        "7f9508563ee21752931e76d8470f5049c026cb3079c4a1c61dfea92bea245063"
    ),
    "MFC-PUB-003-system.json": "8ece72214883cb6be1929c96c40e0591a5ad03b4f0343c267bb281075e6d8fbe",
    "MFC-PUB-003-setpoints.json": (
        "fc29659053d0de65532ef0af8dc91a290889801b1382eefd53edd079c5865b39"
    ),
    "MFC-PUB-004-system.json": "2ec817fa83fe7d0200a66017feb4da16c70d8ea47ec4abf5dddd4110f10ab2f4",
    "MFC-PUB-004-setpoints.json": (
        "4af886c80db209ec6c2c592a30f90917dbd253679bab2c661df4d30127111a10"
    ),
}


def test_public_fixture_checksums_match_source_register() -> None:
    for name, expected in FIXTURE_SHA256.items():
        assert hashlib.sha256((PUBLIC / name).read_bytes()).hexdigest() == expected


@pytest.mark.scientific
@pytest.mark.parametrize(
    ("case_id", "expected_total", "expected_composition", "expected_setpoints"),
    [
        (
            "MFC-PUB-001",
            74.75,
            {
                "C2H2": 0.75 / 74.75,
                "C3H6": 15.0 / 74.75,
                "H2": 1.5 / 74.75,
                "N2": 57.5 / 74.75,
            },
            {
                "C2H2_channel": 0.75,
                "C3H6_channel": 15.0,
                "H2_channel": 1.5,
                "N2_internal_standard": 57.5,
            },
        ),
        (
            "MFC-PUB-002",
            300.0,
            {"D2": 0.025, "H2": 0.025, "N2": 0.95},
            {"5pct_H2_in_N2": 150.0, "5pct_D2_in_N2": 150.0},
        ),
        (
            "MFC-PUB-003",
            25.0,
            {"CO2": 0.19, "H2": 0.76, "He": 0.05},
            {"CO2_channel": 4.75, "H2_channel": 19.0, "He_internal_standard": 1.25},
        ),
        (
            "MFC-PUB-004",
            100.0,
            {"CO": 0.0054, "N2": 0.8946, "O2": 0.1},
            {"N2_5.0": 84.0, "O2_5.0": 10.0, "9pct_CO_in_N2_5.0": 6.0},
        ),
    ],
)
def test_reported_forward_and_same_geometry_inverse(
    case_id: str,
    expected_total: float,
    expected_composition: dict[str, float],
    expected_setpoints: dict[str, float],
) -> None:
    system = load_system(PUBLIC / f"{case_id}-system.json")
    assert system.standard_conditions is None
    assert all(cylinder.mfc is None for cylinder in system.cylinders)

    forward = forward_mix(system, load_setpoints(PUBLIC / f"{case_id}-setpoints.json"))
    assert forward.total_flow == pytest.approx(expected_total)
    assert forward.composition == pytest.approx(expected_composition)
    assert sum(forward.composition.values()) == pytest.approx(1.0)

    inverse = inverse_mix(system, expected_composition, expected_total)
    assert inverse.status is SolutionStatus.EXACT
    assert inverse.setpoints == pytest.approx(expected_setpoints)
    assert "not assessed" in " ".join(inverse.messages)


@pytest.mark.scientific
def test_unknown_standard_conditions_block_amount_flow_conversion() -> None:
    system = load_system(PUBLIC / "MFC-PUB-002-system.json")
    result = forward_mix(system, load_setpoints(PUBLIC / "MFC-PUB-002-setpoints.json"))
    with pytest.raises(InputError, match="unknown"):
        total_molar_flow(result)
    with pytest.raises(InputError, match="unknown"):
        ghsv(result, 1.0)


def test_unknown_mfc_range_does_not_relax_nonnegative_flow() -> None:
    system = load_system(PUBLIC / "MFC-PUB-003-system.json")
    with pytest.raises(InputError, match="negative"):
        forward_mix(system, {"CO2_channel": -1.0, "H2_channel": 20.0})


@pytest.mark.scientific
def test_real_premix_geometry_infeasible_and_approximate_semantics() -> None:
    system = load_system(PUBLIC / "MFC-PUB-002-system.json")
    impossible_target = {"H2": 0.10, "D2": 0.025, "N2": 0.875}

    refused = inverse_mix(system, impossible_target, 300.0)
    assert refused.status is SolutionStatus.INFEASIBLE
    assert refused.setpoints == {}
    assert "not assessed" in " ".join(refused.messages)

    diagnostic = inverse_mix(system, impossible_target, 300.0, allow_approximate=True)
    assert diagnostic.status is SolutionStatus.APPROXIMATE
    assert diagnostic.setpoints
    assert diagnostic.maximum_composition_error is not None
    assert diagnostic.maximum_composition_error >= 0.05 - 1e-7
    assert "not assessed" in " ".join(diagnostic.messages)


@pytest.mark.scientific
def test_downstream_analyzer_dilution_is_not_added_to_reactor_inlet_geometry() -> None:
    system = load_system(PUBLIC / "MFC-PUB-003-system.json")
    with pytest.raises(InputError, match="absent"):
        inverse_mix(system, {"N2": 20.0 / 45.0}, 45.0)
