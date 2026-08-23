# Validation register

| Case | Basis | Expected behavior | Automated evidence |
|---|---|---|---|
| Three-cylinder forward | Hand material balance | 5% CO2, 20% H2, 75% N2 at 200 sccm | `tests/unit/test_mixing.py` |
| Three-cylinder inverse | Unique hand solution | 100/80/20 sccm; exact | `tests/unit/test_mixing.py` |
| Pure-cylinder overdetermined target | Controlled synthetic | 20 sccm H2 + 60 sccm N2 | `tests/unit/test_mixing.py` |
| Unreachable 50% CO2 target | Composition upper bound | infeasible; no successful setpoints | `tests/unit/test_mixing.py` |
| Approximate opt-in | Same unreachable target | labelled approximate with residual | `tests/unit/test_mixing.py` |
| Turndown boundary | Physical input boundary | off accepted; below-minimum nonzero rejected | `tests/unit/test_mixing.py` |
| Standard flow | NIST table / ideal gas | about 7.45e-7 mol/s per sccm at 0 °C, 1 atm | `tests/unit/test_standard_and_derived.py` |
| GUI/CLI/API equality | Cross-layer | same exact core result and export | `tests/integration`, `tests/gui_widget_smoke.py` |

Real-data validation: **pending**. No synthetic test is represented as real
experimental data. Before adoption, a dataset record must include DOI or stable
identifier, license, citation, checksum, files used, and validation scope.
