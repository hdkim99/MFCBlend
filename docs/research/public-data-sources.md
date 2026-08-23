# Public catalytic-feed validation sources

Access date for every record: 2026-08-23. MFCBlend redistributes only small,
manually transcribed input fixtures and exact arithmetic, not the source article
XML or supplementary files. The cited article license applies to the source
artifact; each fixture retains its citation and validation boundary.

No adopted paper defines the temperature and pressure represented by `sccm`, or
the minimum, maximum, and turndown of the MFCs used for the reported experiment.
Those fields are therefore `null` in every public fixture. MFCBlend does not
substitute 0 °C, 25 °C, 1 atm, a nominal controller range, or a turndown ratio.
Composition arithmetic remains possible; molar-flow conversion and MFC-range
feasibility remain unavailable.

## Source artifacts

| Validation ID | Citation and stable identifiers | Article license | File used and SHA-256 |
|---|---|---|---|
| MFC-PUB-001, MFC-PUB-002 | Aireddy, Yu, Cullen, and Ding, *Elucidating the Roles of Amorphous Alumina Overcoat in Palladium-Catalyzed Selective Hydrogenation*, ACS Applied Materials & Interfaces (2022), [DOI 10.1021/acsami.2c02132](https://doi.org/10.1021/acsami.2c02132), [PMCID PMC9164194](https://pmc.ncbi.nlm.nih.gov/articles/PMC9164194/) | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | [Europe PMC full-text XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9164194/fullTextXML), 125,547 bytes, `341397901560af22c0e98a12650b76a5c86d8ce32596f7a7359f82581e331ce4` |
| MFC-PUB-003 | Wolf et al., *A Novel Coprecipitation Path to a High-Performing Ni/MgO Catalyst for Carbon Dioxide Methanation*, ChemSusChem (2025), [DOI 10.1002/cssc.202502052](https://doi.org/10.1002/cssc.202502052), [PMCID PMC12665882](https://pmc.ncbi.nlm.nih.gov/articles/PMC12665882/) | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | [Europe PMC full-text XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12665882/fullTextXML), 133,811 bytes, `2276ec4fe3fd517905ff6f0b961f37fbc8a01ba2483e77985161833438d5706c` |
| MFC-PUB-004 | Röhrens et al., *Surface Speciation in Microwave-Assisted CO Oxidation over Perovskites—The Role of Water and Activation Pretreatment*, ACS Applied Materials & Interfaces (2024), [DOI 10.1021/acsami.4c13212](https://doi.org/10.1021/acsami.4c13212), [PMCID PMC11647750](https://pmc.ncbi.nlm.nih.gov/articles/PMC11647750/) | [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/) | [Europe PMC full-text XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11647750/fullTextXML), 147,766 bytes, `cfdac328581fd65de435aaa9b3c34d095ff4eb4400ee4704522971043c74d9a5` |

The XML checksum covers the exact machine-readable source inspected, not the
publisher landing page. The methods paragraphs were the only portions used to
transcribe feed composition and flow facts.

## MFC-PUB-001 — component channels and N2 internal standard

The paper reports component-labelled C2H2, C3H6, H2, and N2 flow channels at
0.75, 15, 1.5, and 57.5 sccm, respectively, with flow controlled by MKS MFCs.
N2 is identified as the GC internal standard. It does not provide cylinder
certificates or impurity compositions. The fixture therefore treats the
source-labelled channels as nominal single-component streams only for this
arithmetic regression; it does not claim certified gas purity.

```text
Q = 0.75 + 15 + 1.5 + 57.5 = 74.75 sccm
y(C2H2) = 0.75 / 74.75 = 0.0100334448160535
y(C3H6) = 15 / 74.75 = 0.2006688963210702
y(H2)   = 1.5 / 74.75 = 0.0200668896321070
y(N2)   = 57.5 / 74.75 = 0.7692307692307692
H2/C2H2 = 2
```

Forward mode reproduces these values. Inverse mode on the same nominal channel
geometry recovers 0.75/15/1.5/57.5 sccm to floating-point tolerance. “Exact”
means exact material-balance reconstruction only; controller-range feasibility
was not assessed.

## MFC-PUB-002 — two premixed cylinders

The same paper explicitly reports 150 sccm of 5% H2/N2 and 150 sccm of 5%
D2/N2 for an H–D exchange experiment.

```text
Q = 150 + 150 = 300 sccm
component H2 = 150(0.05) = 7.5 sccm-equivalent
component D2 = 150(0.05) = 7.5 sccm-equivalent
component N2 = 150(0.95) + 150(0.95) = 285 sccm-equivalent
y(H2) = 0.025; y(D2) = 0.025; y(N2) = 0.95
```

Forward mode closes to unity and same-geometry inverse mode recovers 150/150
sccm. A source-geometry negative control requests 10% H2, 2.5% D2, and 87.5%
N2. It is compositionally infeasible because neither premix contains more than
5% H2. Default inverse mode returns `infeasible` and no setpoints. Explicit
approximate mode returns a diagnostic 289.173228346457/0 sccm solution with
5% H2, 0% D2, 95% N2, maximum fraction error 0.075, and total-flow error
10.826771653543 sccm. It remains labelled `approximate` and its undocumented
MFC-range feasibility is not assessed.

## MFC-PUB-003 — methanation feed and analyzer-boundary check

The paper reports a reactor inlet of 4.75 sccm CO2, 19 sccm H2, and 1.25 sccm
He internal standard to each parallel reactor. It separately reports adding
20 sccm N2 to the *product* stream before GC sampling. The N2 stream is not a
reactor-inlet cylinder in this fixture.

```text
Q(inlet) = 4.75 + 19 + 1.25 = 25 sccm
y(CO2) = 0.19; y(H2) = 0.76; y(He) = 0.05
H2/CO2 = 4
```

Forward and same-geometry inverse calculations reproduce 4.75/19/1.25 sccm.
An attempt to target N2 with the inlet geometry is rejected because N2 is
absent from every inlet stream. MFCBlend does not combine the 20 sccm analyzer
dilution with the reactor feed, nor estimate the reacted product composition.

## MFC-PUB-004 — CO premix plus pure diluent and oxidant

The paper reports a nominal dry gas feed of 84 sccm N2 (5.0 purity), 10 sccm O2
(5.0 purity), and 6 sccm of 9% CO in N2 (5.0), delivered by MFCs.

```text
Q = 84 + 10 + 6 = 100 sccm
component CO = 6(0.09) = 0.54 sccm-equivalent
component N2 = 84 + 6(0.91) = 89.46 sccm-equivalent
y(CO) = 0.0054 = 5400 ppm; y(O2) = 0.1; y(N2) = 0.8946
```

The article describes the CO concentration as approximately 5000 ppm. Exact
arithmetic from its reported setpoints and 9% premix is 5400 ppm. MFCBlend
records the 400 ppm difference as a rounding/definition difference and does not
alter a coefficient to force agreement. The adopted fixture is dry-basis only:
the paper's separately metered water injection and measured wet concentration
are outside MFCBlend 0.1.0's condensable-feed scope.

## Minimal fixture checksums

| File | SHA-256 |
|---|---|
| `MFC-PUB-001-system.json` | `75c25661eee1845dd40009e524f7da26a77a443b007b9f7d9d41763dc838ba80` |
| `MFC-PUB-001-setpoints.json` | `f4dcfd1f6e505d61c170cc41f4f2a219b74ae1fb5ce04b5f8d3b54400c6e4ed0` |
| `MFC-PUB-002-system.json` | `0b1fdba131e87824f110e2300c0c2b124eb6a3ba542867346191c339b544e693` |
| `MFC-PUB-002-setpoints.json` | `7f9508563ee21752931e76d8470f5049c026cb3079c4a1c61dfea92bea245063` |
| `MFC-PUB-003-system.json` | `8ece72214883cb6be1929c96c40e0591a5ad03b4f0343c267bb281075e6d8fbe` |
| `MFC-PUB-003-setpoints.json` | `fc29659053d0de65532ef0af8dc91a290889801b1382eefd53edd079c5865b39` |
| `MFC-PUB-004-system.json` | `2ec817fa83fe7d0200a66017feb4da16c70d8ea47ec4abf5dddd4110f10ab2f4` |
| `MFC-PUB-004-setpoints.json` | `4af886c80db209ec6c2c592a30f90917dbd253679bab2c661df4d30127111a10` |

Automated evidence is in `tests/public_data/test_public_feed_cases.py`. The
MFC-PUB-003 forward fixture is also used for the native Tk GUI workflow and
export smoke test; GUI, CLI, and API all call the same application service.
