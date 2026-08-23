# Scientific basis and conventions

## Linear material balance

For a nonreacting mixer at steady state, species molar flow is additive. A
cylinder's composition vector forms one column of matrix `A`; MFC flows form
vector `q`. Forward mode computes `Aq`. Inverse mode requests selected species
flows and total flow and solves a bounded linear system.

Code: `src/mfcblend/core/mixing.py`.

SciPy's bounded linear least-squares implementation is documented at:

- SciPy, [`scipy.optimize.lsq_linear`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.lsq_linear.html), accessed 2026-08-23.

This numerical method is not a chemical model. Chemical assumptions enter in
the cylinder compositions, common molar-flow basis, and ideal mixing.

## Off-or-operating MFC constraints

MFCBlend treats each MFC as either off (`q = 0`) or inside the supplied operating
interval. The tool does not invent a minimum from a device class. If the user
provides a turndown ratio, it is interpreted explicitly as full scale divided by
minimum controllable flow.

When a source does not report an MFC range, JSON records `"mfc": null`.
Forward mode then checks only that the reported setpoint is nonnegative. Inverse
mode uses a nonnegative mathematical bound but explicitly states that physical
range/turndown feasibility was not assessed. An absent upper bound is not an
inferred infinite-capacity instrument.

Because zero plus a nonzero interval is not one continuous bound, active subsets
are enumerated rather than silently permitting a below-minimum setpoint. Version
0.1.0 limits this exact enumeration to 16 MFCs.

## Standardized volumetric flow

The amount-flow conversion is the ideal-gas relation

```text
n_dot = P_ref Q_ref / (R T_ref)
```

where pressure is absolute. Reference-state conversion preserves this molar
flow. No compressibility factor is applied.

Sources:

- NIST, [Pressure and Gas Flow Unit Conversions](https://www.nist.gov/pml/owm/metric-si/unit-conversion/pressure-and-gas-flow-unit-conversions), updated 2025-07-28. NIST states that its table's volume-flow units use an ideal gas at 101325 Pa and 0 °C, and warns that `sccm` sometimes assumes a different temperature.
- IUPAC Gold Book, [standard pressure](https://goldbook.iupac.org/terms/view/S05921), DOI [10.1351/goldbook.S05921](https://doi.org/10.1351/goldbook.S05921). IUPAC recommends 100000 Pa, while 101325 Pa was historically common.
- BIPM, [The International System of Units (SI), 9th edition](https://www.bipm.org/en/publications/si-brochure). The molar gas constant has an exact value following the fixed Boltzmann and Avogadro constants.

These differing conventions are why the input schema never assigns meaning from
`sccm` or `nml/min` alone. A known convention records both reference temperature
and reference pressure. An unreported convention records
`"standard_conditions": null`; composition arithmetic remains available, but
molar-flow conversion and reference-state GHSV raise an explicit input error.

## Derived quantities

- Ideal partial pressure: `p_i = y_i P`.
- GHSV: reference volumetric feed flow per catalyst-bed volume, reported in
  `h^-1`; the result retains the flow reference conditions. It is not the actual
  reactor-temperature volumetric velocity.

GHSV usage is consistent with the US EPA's *Control Technology Appendices for
Pollution Control Manuals*, which describes gas hourly space velocity as unit
volumetric flow per unit catalyst volume:
[EPA document](https://nepis.epa.gov/Exe/ZyPURL.cgi?Dockey=20007RNK.TXT).

## Interpretation boundary

`exact` means the requested mathematical balance is satisfied within the stated
tolerances and MFC constraints. It does not validate cylinder certificates,
actual MFC accuracy, calibration correction factors, mixing dynamics, gas
compatibility, or process safety. MFCBlend deliberately contains no flammability
or explosion-limit model.
