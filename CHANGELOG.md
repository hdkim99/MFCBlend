# Changelog

All notable changes will be documented here. Versioning follows semantic
versioning while the scientific interface remains in 0.x development.

## [0.1.1] — 2026-08-23

- Four DOI-linked public catalytic-feed regressions with provenance, license,
  source checksums, exact arithmetic, and rejected-candidate register.
- Explicit unknown states for unreported standard-flow reference conditions and
  MFC ranges; dependent conversions are blocked and range feasibility is not
  claimed.
- Preserve the unreported-range warning on exact, approximate, and infeasible
  inverse-planning paths. No standard condition, MFC range, or turndown value is
  inferred.

## [0.1.0] — 2026-08-23

- Initial forward and constrained inverse gas-feed planning core.
- Explicit MFC ranges, turndown, reference conditions, and infeasibility status.
- Python API, CLI, Tkinter GUI, JSON/CSV export, and result plotting.
- DGX and macOS verification workflows and scientific regression tests.
