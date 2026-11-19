# Wrinkle Geometry Calculator

A source preview for **NX 2412** and **CATIA V5 R32**. Both entries calculate a wrinkle profile and open the same illustrated English report in the Windows default browser. The report runs offline.

- In NX, play [NX_WrinkleCalculator.py](ready-to-run/NX_WrinkleCalculator.py) as a Python journal. Enter your values in its Windows dialog and select **Calculate**.
- In CATIA, run [CATIA_WrinkleCalculator.CATScript](ready-to-run/CATIA_WrinkleCalculator.CATScript) from a **Directories** macro library. Follow the native input prompts.

Each startup file contains its calculation core and the report template. NX keeps a copy of the results in the dialog. CATIA shows three text dialogs if the browser report cannot open. Execution inside either CAD host remains unverified, along with installation, native UI imports, VBA compilation, and local licensing.

The calculator reproduces the specified Excel method. It first finds the cosine amplitude from a 1,000-segment polyline, then fits three circular arcs and two straight tangents by minimizing vertical deviations without a length constraint. The calculation requires no Excel installation, Solver, SciPy, or other third-party package.

```sh
python3 -m unittest discover -s tests -v
python3 -m wrinkle 40 30 --thickness 2
```

CI checks Python 3.10, 3.11 and 3.13. The NX journal uses the Python interpreter bundled with NX and requires `ctypes`. The CATIA macro requires VBScript and permission to run macros. The preview accepts lengths from 0.001 to 1,000,000 mm with `l2 <= l1 <= 2*l2`, and optional wall thickness from 0 to 1,000,000 mm. These are numerical limits.

| Quantity for l1 = 40 mm and l2 = 30 mm | Approximate result |
|---|---:|
| Cosine amplitude A, from the midline to the crest | 6.139413268 mm |
| Radius R of the fitted circular arcs | 5.0322554 mm |
| Flank angle φ | 49.8407463° |
| Fitted profile height h | 12.2342750 mm |
| Straight segment s per side | 11.3319680 mm |
| Fitted polyline length | 40.1738373 mm |
| Analytical length of the fitted profile | 40.1738725 mm |
| Fitted polyline length deviation from l1 | **+0.434593%** |
| RMS and maximum vertical shape deviations at the sample points | 0.096220 / 0.181006 mm |

In the reference case, `l1` is the unfolded target length measured along the cosine profile, and `l2` is the horizontal distance between its endpoints. The fit exceeds the 0.1% length deviation target. The reported shape deviations measure vertical distances at the 1,001 sample points.

For 2 mm wall thickness, the simplified strain estimates are 13.46524% using the Excel cosine radius, 26.93048% using the corrected cosine radius, and 19.87181% using the fitted arc radius. The Excel radius is twice the mathematically correct cosine radius. The report identifies each result separately. These `t/(2r)` estimates establish neither material approval nor crack resistance.

- [NX 2412 startup guide](docs/NX2412.md)
- [CATIA V5 R32 startup guide](docs/CATIA-V5-R32.md)
- [Calculation method and result fields](docs/MATHEMATICS.md)
- [Validation performed and its limits](docs/VALIDATION.md)
- [Source packages and release procedure](docs/RELEASES.md)

Keep the original workbook out of this repository and all packages. The repository uses `.gitignore`, a staged-file audit and a release allowlist. Enable the local commit hook with the following command.

```sh
git config core.hooksPath .githooks
```

The reference CSV contains the supplied numerical cases and scaled examples. CAD software and its licenses are supplied separately by the respective vendors.
