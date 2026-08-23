from __future__ import annotations

import pytest

from mfcblend.core import (
    StandardConditions,
    convert_reference_flow,
    forward_mix,
    ghsv,
    molar_flow,
    partial_pressures,
    total_molar_flow,
)
from mfcblend.io import load_setpoints, load_system


@pytest.mark.scientific
def test_nist_style_sccm_molar_flow_at_zero_c_one_atm() -> None:
    # NIST tabulates about 7.45e-7 mol/s per sccm at 0 °C and 1 atm.
    value = molar_flow(1.0, "sccm", StandardConditions(273.15, 101325))
    assert value == pytest.approx(7.4358e-7, rel=2e-5)


def test_reference_condition_conversion_preserves_molar_flow() -> None:
    zero_c = StandardConditions(273.15, 101325)
    twenty_five_c = StandardConditions(298.15, 101325)
    converted = convert_reference_flow(100, "sccm", zero_c, twenty_five_c)
    assert converted == pytest.approx(109.15248, rel=1e-6)
    assert molar_flow(100, "sccm", zero_c) == pytest.approx(
        molar_flow(converted, "sccm", twenty_five_c)
    )


def test_partial_pressure_and_ghsv_use_explicit_bases() -> None:
    system = load_system("examples/co2_hydrogen_system.json")
    result = forward_mix(system, load_setpoints("examples/setpoints_5co2_20h2.json"))
    assert partial_pressures(result.composition, 200000)["CO2"] == pytest.approx(10000)
    assert ghsv(result, 2.0) == pytest.approx(6000)
    assert total_molar_flow(result) == pytest.approx(200 * 7.4358e-7, rel=2e-5)
