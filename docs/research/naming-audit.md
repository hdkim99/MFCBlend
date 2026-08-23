# Naming and competitive audit

Audit date: 2026-08-23. Searches covered exact and similar names in GitHub
repositories, PyPI's JSON project endpoint, general web results, scientific
software, commercial products, and Python/macOS GUI terminology. A search with no
single hit was not treated as sufficient evidence; exact PyPI endpoints and
several query forms were checked.

## Project C

- Working name: GasFeed
- Candidates reviewed: 12
- Selected name: MFCBlend
- GitHub repository: `MFCBlend`
- Python package: `mfcblend`
- PyPI candidate: `mfcblend`
- Selection reason: concise, pronounceable, directly evokes MFC-constrained gas
  blending, and is substantially more searchable than GasFeed.
- Known naming risks: `MFCblend` occurs as a descriptive downstream-controller
  tag in one scientific supporting-information document. No same-name software,
  Python package, Qt/macOS framework, or prominent commercial product was found.

| Candidate | Assessment | Finding |
|---|---|---|
| GasFeed | MINOR RISK | PyPI name free, but generic and mixed with unrelated `GasFeed*` repositories/pages. |
| MFCBlend | CLEAR / minor residual | PyPI name free; no software/package collision; one descriptive equipment tag. |
| MFCMix | MINOR RISK | PyPI name free; compact but `MFC` also names an unrelated multiphase-flow solver. |
| MixMFC | MINOR RISK | PyPI name free; less natural pronunciation/search intent. |
| FeedMixLab | CLEAR | PyPI name free; descriptive but longer and less specifically tied to MFCs. |
| ReactorFeed | HIGH RISK | Existing ReactorFeed torrent/RSS service and generic process term. |
| GasMixtureLab | CLEAR | PyPI name free; descriptive but long and not reactor/MFC specific. |
| FlowBlend | HIGH RISK | Existing FlowBlend business/trademark/product and FlowBlending ML term. |
| BlendFlow | HIGH RISK | Existing commercial Blender extension, data product, and portable-blender brands. |
| FeedComposer | MINOR RISK | PyPI name free but generic “feed” ambiguity and composer ecosystem confusion. |
| FlowRecipe | MINOR RISK | PyPI name free; “flow” is broad and search intent is weak. |
| ReactorMix | MINOR RISK | PyPI name free; suggests a reactor mixing model rather than feed planning. |

## Competitive landscape and differentiation

- [Catalight](https://catalight.readthedocs.io/en/stable/equipment_guides.html)
  contains Alicat-linked gas control and gas-mixture handling; its documented MFC
  count is hard-coded and it is coupled to hardware/control workflows.
- Vendor MFC software and integrated reactor platforms provide instrument control
  and configuration for their own equipment.
- Full simulators such as Cantera and commercial reactor/process packages solve
  broader reacting systems rather than a small vendor-neutral cylinder/MFC
  feasibility problem.

MFCBlend's minimum useful scope is deliberately narrower: offline, vendor-neutral
forward verification and constrained inverse planning with explicit reference
conditions and honest infeasibility. It does not communicate with hardware or
claim process-safety validation.

## GUI naming/dependency risk

The name does not collide with Tk, Tcl, Qt, PyQt, PySide, or Matplotlib. The GUI
uses Tkinter/ttk because the workflow needs forms, a result table, and export—not
a Qt-specific capability. Qt binding/version/plugin risks are structurally absent;
the CLI and core do not import either GUI or plotting modules.
