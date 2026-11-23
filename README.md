# Wrinkle Geometry Calculator

A source preview for **NX 2412** and **CATIA V5 R32**. Both entries calculate a wrinkle
profile and open the same illustrated English report in the Windows default browser. The
report runs offline.

- In NX, play [NX_WrinkleCalculator.py](ready-to-run/NX_WrinkleCalculator.py) as a
  Python journal. Enter your values in its Windows dialog and select **Calculate**.
- In CATIA, run
  [CATIA_WrinkleCalculator.CATScript](ready-to-run/CATIA_WrinkleCalculator.CATScript)
  from a **Directories** macro library. Enter the dimensions in one Windows form.
  If Windows PowerShell is blocked, enter all values in a single native prompt.

Both windows accept l1, l2, wall thickness, and optional elongation at fracture A [%].
The input forms sketch developed length L1, projected length L2, and wall thickness t.
When both thickness and A are entered, the report compares estimated strain with A in
percentage points. A is a tensile-test reference, not a cracking limit.

Each startup file contains its calculation core and the report template. NX keeps a copy
of the results in the dialog. CATIA shows text results if the browser report cannot
open. Execution inside either CAD host remains unverified, along with
installation, native UI imports, VBA compilation, and local licensing.

The calculator reproduces the specified Excel method. It first finds the cosine
amplitude from a 1,000-segment polyline, then fits three circular arcs and two straight
tangents by minimizing vertical deviations without a length constraint. The calculation
requires no Excel installation, Solver, SciPy, or other third-party package.

```sh
python3 -m unittest discover -s tests -v
python3 -m wrinkle 40 30 --thickness 2
```

CI checks Python 3.10, 3.11 and 3.13. The NX journal uses the Python interpreter bundled
with NX and requires `ctypes`. The CATIA macro requires VBScript and permission to run
macros. The preview accepts lengths from 0.001 to 1,000,000 mm with `l2 <= l1 <= 2*l2`,
and optional wall thickness from 0 to 1,000,000 mm. These are numerical limits.

| Quantity for l1 = 40 mm, l2 = 30 mm, and t = 2 mm | Report value |
|---|---:|
| Undeformed wall length l1 | 40.00 mm |
| Deformed wall length l2 (neutral fibre) | 30.00 mm |
| Radius R of each fitted circular arc | 5.03 mm |
| Fitted profile height h | 12.23 mm |
| Flank angle (phi) | 49.84 deg |
| Cosine curvature at the crest | 3.71 mm / 26.93% |

The calculator uses `l1` as the target length along the cosine. It uses `l2` as the
horizontal span between the endpoints of the deformed neutral-fibre profile. **More
information** opens the length and shape comparison. Values in the report are rounded
to two decimal places.

**Cosine bending estimate** shows the minimum radius of the neutral-fibre cosine
and the estimated outer-fibre bending strain when wall thickness is supplied.
The radius is distinct from the fitted circular-arc radius. The strain uses
the simplified model `t/(2R)` and is not a crack prediction or material approval.
The report does not assign a fracture risk band.

- [NX 2412 startup guide](docs/NX2412.md)
- [CATIA V5 R32 startup guide](docs/CATIA-V5-R32.md)
- [Calculation method and result fields](docs/MATHEMATICS.md)
- [Validation performed and its limits](docs/VALIDATION.md)
- [Source packages and release procedure](docs/RELEASES.md)

Keep the original workbook out of this repository and all packages. The repository uses
`.gitignore`, a staged-file audit and a release allowlist. Enable the local commit hook
with the following command.

```sh
git config core.hooksPath .githooks
```

The reference CSV contains the supplied numerical cases and scaled examples. CAD
software and its licenses are supplied separately by the respective vendors.
