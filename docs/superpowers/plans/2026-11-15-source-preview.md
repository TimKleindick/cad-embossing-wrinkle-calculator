# Excel-compatible source preview plan

The supplied direction fixes the design: Python/NX Open + Block Styler and VBA/CATIA UserForm, separate pure cores, no CAD geometry or Excel runtime. This empty repository needs no migration. A fresh clone and feature branch isolate the work.

1. `reference/cases.csv`, `tests/test_core.py`: encode supplied 40/30 numbers, a flat case, homogeneity, invalid inputs, convergence, geometric continuity and slope, and explicit Excel/corrected radius conventions. First run against a missing-behavior skeleton and record failures.
2. `wrinkle/core.py`: normalize by l2; bisection of cosine polygon length; bounded physical form-fit using deterministic Nelder-Mead; report sampled and analytic lengths, errors, fit residuals and simplified strain estimates. No length constraint on form fit. `wrinkle/__main__.py` supplies an offline CLI.
3. `cad/catia/WrinkleCore.bas`: portable VBA/VBScript-compatible pure calculations, using identical algorithm and shared numeric references. Windows `cscript` runs this actual source after removing only the VBA module attribute; this is not proof of VBA compilation or CATIA import.
4. `cad/nx/wrinkle_dialog.py`: consume a locally created DLX. `cad/catia/Launch.bas` and `UserForm-code.txt`: consume a manually created native form. No invented DLX/CATVBA/FRX binary. `docs/NX2412.md`, `docs/CATIA-V5-R32.md` explain creation, inputs, verification and unresolved host/licensing limits.
5. `tools/package_preview.py`, `tests/test_packaging.py`: explicit path allowlist, reject spreadsheets by name and content, binary/ZIP/OLE payloads and symlinks; audit the Git index before publishing. Tests first, including disguised workbook and out-of-tree attacks.
6. CI runs Python and Windows script reference checks with read-only permissions. Release builds only a source-preview ZIP after checks, an explicit manual acknowledgement and an existing main-commit tag; publishing job has only contents:write and publishes the two exact assets. No automatic release, no broad artifact paths.
7. Independent review and local full suite; inspect archives and staged paths. Record evidence, Conventional Commit and push feature branch. Inspect GitHub CI. No merge or tag requested.

Numerical envelope will be explicit and validated, including a flat limit. Excel Solver stopping behavior cannot be bit-identical without its algorithm/settings; compare supplied numbers using declared tolerances and show any difference. A 0.1% form-fit length target must never change the standard objective.
