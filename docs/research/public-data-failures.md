# Public-data search and failure register

Search date: 2026-08-23. The search covered Europe PMC/PMC full text, publisher
article and supplementary pages, Zenodo, Mendeley Data, Figshare, Dryad, OSF,
and general web search. Query families combined `catalytic reactor`, `mass flow
controller` or `MFC`, `sccm`, `premix`, `internal standard`, `diluent`, and
species-specific terms. A GitHub or repository fixture was not accepted merely
because it contained plausible numbers; an attributable real experiment was
required.

## Rejected or limited candidates

| Register ID | Candidate | Artifact provenance | Decision and reason |
|---|---|---|---|
| MFC-PUB-R001 | Mohammad, Aravamudhan, and Kuila, *Atomic Layer Deposition of Cobalt Catalyst for Fischer–Tropsch Synthesis in Silicon Microchannel Microreactor* | [DOI 10.3390/nano12142425](https://doi.org/10.3390/nano12142425), [PMCID PMC9320865](https://pmc.ncbi.nlm.nih.gov/articles/PMC9320865/), CC BY 4.0; Europe PMC XML 80,689 bytes, SHA-256 `d5961857661619e8e2553e7224c8e173a660b7c9bf50313ec90d892152dff898` | Rejected as an exact fixture. The paper provides H2/CO and N2 controller ranges and a 2:1 H2:CO ratio, but not a complete simultaneous setpoint vector/total flow for the reported run. Inventing the missing total or N2 setpoint would defeat validation. |
| MFC-PUB-R002 | Narula et al., *Heterobimetallic Zeolite, InV-ZSM-5, Enables Efficient Conversion of Biomass Derived Ethanol to Renewable Hydrocarbons* | [DOI 10.1038/srep16039](https://doi.org/10.1038/srep16039), [PMCID PMC4630624](https://pmc.ncbi.nlm.nih.gov/articles/PMC4630624/), CC BY 4.0; Europe PMC XML 85,330 bytes, SHA-256 `0459e486d9e1e5536cd9f5078d91ea243b031f781937c5af1a0fd6fadeae450c` | Rejected from the gas-mixer fixture set. It reports N2 as a 5 sccm analytical internal standard while the reactant is delivered by a liquid syringe pump. MFCBlend does not model liquid vaporization or the resulting wet/gas feed. |
| MFC-PUB-R003 | Kruger et al., *Integrated conversion of 1-butanol to 1,3-butadiene* | [DOI 10.1039/c8ra02977f](https://doi.org/10.1039/c8ra02977f), [PMCID PMC9081732](https://pmc.ncbi.nlm.nih.gov/articles/PMC9081732/); license not declared in the inspected Europe PMC XML; XML 59,547 bytes, SHA-256 `a06722cd5baf34f882f242942e29ef02227d9e818e95bb314723a8555185896d` | Rejected from the gas-only core. The reported setup combines liquid 1-butanol injection with a gas stream; reproducing it requires a vaporizer/phase model that 0.1.0 explicitly does not provide. The unclear XML license also argues against redistributing source material. |
| MFC-PUB-R004 | NCBI OA package URL returned by the OA API for PMC9164194 | NCBI OA API metadata identified CC BY, but the attempted HTTPS translation of the FTP object returned a 990-byte “Object not found” XML response | Retrieval path rejected. Validation used the stable Europe PMC full-text XML endpoint instead; the failed object was neither cached nor treated as research data. |

Searches of general-purpose data repositories did not yield a better licensed,
machine-readable gas-feed dataset that simultaneously reported cylinder
composition, every setpoint, stream location, reference T/P, and MFC ranges.
This absence is not filled by synthetic metadata. The adopted article-method
cases are public real experiments, while their unknown fields remain explicit.

## Failure-first implementation record

Before scientific-core changes, the new public regression suite was run against
the 0.1.0 baseline. All seven initial cases failed because the JSON loader
rejected `standard_conditions: null` with `standard_conditions must be a JSON
object`. After the minimal reference-condition change, the same cases failed at
the next real boundary because `mfc: null` was rejected. Only then was the model
extended to preserve an unreported MFC range. The repaired suite passed without
assigning substitute temperatures, pressures, MFC limits, or turndown values.

A further message-level regression showed that default infeasible output still
said “MFC operating ranges” without disclosing that the source ranges were
unknown. That regression failed first and was then repaired so exact,
approximate, and infeasible paths all retain the “range feasibility was not
assessed” qualification.

## Failure and interpretation boundaries discovered

- `sccm` reference temperature and pressure are unreported in MFC-PUB-001
  through MFC-PUB-004. Amount-flow conversion and reference-state GHSV are
  blocked rather than silently defaulted.
- MFC minimum, maximum, and turndown are unreported in all adopted cases.
  Forward calculations enforce nonnegative setpoints only; inverse setpoints
  are conditional material-balance solutions and explicitly say range
  feasibility was not assessed.
- MFC-PUB-004's exact nominal CO arithmetic is 5400 ppm, whereas the source uses
  an approximate 5000 ppm description. This is retained as a definition/rounding
  difference, not “corrected” by an undocumented coefficient.
- MFC-PUB-003 adds N2 downstream of the reactor before GC analysis. Treating it
  as a reactor-inlet diluent would be a geometry error, so a regression test
  rejects N2 targets for the inlet system.
- Approximate mode is never promoted to exact. For the MFC-PUB-002 impossible
  target, default behavior returns no setpoints; opt-in approximate output
  reports both composition and total-flow residuals.
- None of these validations establishes gas compatibility, flammability,
  calibration accuracy, dynamics, or process safety.
