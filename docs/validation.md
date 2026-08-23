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
| MFC-PUB-001 | Public catalytic selective-hydrogenation methods | four source-labelled channels, N2 internal standard; forward and same-geometry inverse | `tests/public_data/test_public_feed_cases.py` |
| MFC-PUB-002 | Public H-D exchange methods | two 5% premixes; forward/inverse plus infeasible geometry negative control | `tests/public_data/test_public_feed_cases.py` |
| MFC-PUB-003 | Public CO2-methanation methods | 4.75/19/1.25 sccm inlet, He internal standard; downstream N2 boundary | `tests/public_data/test_public_feed_cases.py` |
| MFC-PUB-004 | Public CO-oxidation methods | pure N2/O2 and 9% CO/N2 premix; exact dry-basis 5400 ppm | `tests/public_data/test_public_feed_cases.py` |

Four public real-experiment feed cases are adopted. Source DOI/PMCID, license,
file URL and checksum, exact calculations, files used, and validation scope are
recorded in [`research/public-data-sources.md`](research/public-data-sources.md).
Search failures and rejected candidates are recorded in
[`research/public-data-failures.md`](research/public-data-failures.md). Synthetic
tests remain labelled as synthetic.

Local public-case verification on 2026-08-23 used macOS 27.0 arm64, Python
3.14.7, and Tk 9.0. MFC-PUB-003 passed real window creation, application-service
calculation, JSON export, close, and process exit both from the source tree and
a clean 0.1.0 wheel installation. This local check supplements, rather than
replaces, the GitHub macOS matrix.
