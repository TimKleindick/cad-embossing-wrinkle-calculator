# Validation record

The original verification took place on November 15, 2026, on a Mac running Python 3.13.1. The empty repository was cloned into a separate checkout on `feat/excel-compatible-source-preview`. The original checkout contained no `AGENTS.md` or `.agents/skills`. The GitHub identity `TimKleindick` and private repository status were confirmed at that time.

## Original local checks

- The nine solver tests first ran against explicit `NotImplementedError` placeholders. They produced 28 expected subtest errors, then passed after implementation. Coverage includes the reference values, 1000-segment convention, flat case, invalid inputs, homogeneous scaling, radius conventions, convergence, symmetry, endpoints, and tangency.
- Four package tests initially produced 11 errors against placeholders, then passed. Further cases exercise misleading staged blobs, a tampered manifest, and unexpected archive entries. Workbook bytes used by those tests are synthetic signatures.
- The CLI test first failed with `No module named wrinkle.__main__`, then passed its JSON reference and invalid input cases.
- `python3 -m unittest discover -s tests -v` passed with 16 tests initially and 17 after the cross-platform ZIP regression test.
- `python3 -m compileall -q wrinkle cad/nx tools` checked Python syntax without loading NX.
- `python3 -m tools.independent_check` used a nested golden-section search with a coarse angle search and Simpson integration of the continuous cosine length. It computes expected values independently of the production Nelder-Mead solver.

The independent reference fit gave A = 6.139413268036 mm, R = 5.032255388979 mm, φ = 49.840746273028°, height = 12.234275003659 mm, straight length = 11.331968037174 mm per side, polyline length = 40.173837278632 mm, and analytical length = 40.173872488835 mm. Differences from the supplied Excel values were less than `1.1e-7` in the corresponding units. The production fit gave approximately 40.173837277456 mm sampled and 40.173872487659 mm analytically. The reference comparison establishes agreement for the tested cases.

| Diagnostic segment count | A [mm], independent calculation | Fitted polyline length [mm] |
|---:|---:|---:|
| 500 | 6.139443564951 | 40.173812471217 |
| **1000, default** | **6.139413268036** | **40.173837278632** |
| 2000 | 6.139405693840 | 40.173842859126 |
| 4000 | 6.139403800293 | 40.173843953457 |

The Excel-compatible reference case has a length error of +0.434593%, exceeding the 0.1% target. The calculation preserves the supplied sampling and fitting rules. The inputs for this validation were the supplied formulas and numbers.

## Original Windows CI

All three jobs passed on Ubuntu with Python 3.11 and 3.13 and on Windows with Python 3.13. Each job passed 16 Python tests, the staged blob audit, syntax checking, and allowlisted package creation. The Windows job ran the actual `.bas` core with initial locales 1033 (en-US) and 1031 (de-DE). It checked three shared references plus scaling, flat and near-flat cases, the range boundary, input validation, strain, profile shape, and tangency. The deliberately altered Excel-radius formula triggered `FAIL: Excel strain` as expected. No artifacts were uploaded. [CI run 43723275112 for `7219095`](https://github.com/TimKleindick/cad-embossing-wrinkle-calculator/actions/runs/43723275112)

The following run passed all three jobs and both locale checks again, with zero artifact uploads. Platform-specific hashes initially came from checkout line endings and the ZIP creator system. `.gitattributes` now enforces LF, and the builder sets a common POSIX creator system. A regression test produced different bytes before that fix and passed afterward. The VBA test was written first, but the pre-implementation failure could not be exercised on the Mac. `cscript.exe` exercises the portable `.bas` core after removing export metadata. Native VBA compilation remains unverified. [CI run 43723532495 for `557fa80`](https://github.com/TimKleindick/cad-embossing-wrinkle-calculator/actions/runs/43723532495)

## Standalone CAD entry checks

`tools/build_entries.py` embeds `wrinkle/core.py` and `cad/catia/WrinkleCore.bas` in `ready-to-run/NX_WrinkleCalculator.py` and `ready-to-run/CATIA_WrinkleCalculator.CATScript`. Four new tests first failed with the missing entry components and then passed. The full local suite reached 21 passing tests, with additional checks of Python syntax, independent mathematics, and generated-file freshness. The NX journal calculated successfully after being copied alone into an empty directory and run with isolated Python.

Four CI jobs passed on Ubuntu with Python 3.10, 3.11, and 3.13 and on Windows with Python 3.13. Windows opened the generated Win32 dialog from a single copied file and checked 40/30/2, comma decimals, invalid input clearing the prior result, the flat case without thickness, and closing. The generated CATScript passed controlled input/output, cancellation, errors, and result pages in en-US and de-DE. At this stage, the harness removed the `Language` assignment and repositioned `Option Explicit` before testing the CATScript body. The Excel-radius negative control still failed as intended, and the true core passed. [CI run 43726095118 for `9627bab`](https://github.com/TimKleindick/cad-embossing-wrinkle-calculator/actions/runs/43726095118)

All four jobs and the local Mac produced the same ZIP with SHA-256 `86218be6175f5a0b04d8d40006bf633940ab212b0c609c2cd42a2c425dbfdc87`. That package had 32 explicitly named sources, including both standalone entries and the optional designer guides. The extracted local ZIP passed freshness checking and all 21 tests. The CI run uploaded zero artifacts.

## CATScript startup correction

A workstation test in CATIA V5 R32 reported `ScriptingERR_1002` at `Option Explicit` on line 2. The original file began with a `Language` assignment. The Windows harness removed both lines and therefore missed this startup issue. The generator now emits `Option Explicit` first and omits `Language`. The regression test caught the old preamble and passed with the corrected file. CI now checks the delivered CATScript directly with `cscript` before running numerical and dialog-flow tests. The four jobs passed for the corrected commit, including compilation of the original preamble in Windows Script Host. [CI run 44508712331 for `f19c410`](https://github.com/TimKleindick/cad-embossing-wrinkle-calculator/actions/runs/44508712331)

## Illustrated CATIA result baseline

The illustrated CATIA result was rendered locally in a browser for the 40/30, flat 30/30, and range-boundary 60/30 cases. The Windows Script Host tests passed compilation, report data, text fallback, error handling, and cancellation in en-US and de-DE. The four CI jobs passed after the independent Win32 NX dialog job was rerun. [CI run 44509605213 for `b6690ce`](https://github.com/TimKleindick/cad-embossing-wrinkle-calculator/actions/runs/44509605213)

## CAD workstation checks still open

End-to-end execution in NX 2412 and CATIA V5 R32, including opening the offline browser report from each CAD host, remains to be verified on the target workstation. Other open checks include NX Python integration, the optional Block Styler designer and DLX import, the optional CATIA VBA compiler and Forms workflow, saving and reimporting CATVBA, licenses, and workstation installation. The source package contains no CAD binaries. The release publishing path has yet to be exercised.

See the [NX 2412 guide](NX2412.md) and [CATIA V5 R32 guide](CATIA-V5-R32.md) for the workstation checks and values to record. A Windows dialog or Script Host pass confirms the standalone code on that runner. CAD-host verification requires running the corresponding workstation checks.

## Shared English NX and CATIA report

Both standalone launchers embed `cad/result.html` and send it the numerical results and sampled profile from their existing calculation cores. Local verification passed 24 tests. Headless Chrome rendered the 40/30 mm reference and flat cases. Windows CI exercises the NX dialog, report creation and browser error fallback through the generated NX entry file. Opening the report directly from the installed CAD applications remains a workstation check.
