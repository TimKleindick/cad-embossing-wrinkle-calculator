# Optional CATIA V5 R32 UserForm setup

The [standalone CATScript](CATIA-V5-R32.md) is the standard entry and produces the illustrated report. This optional workstation procedure builds a native CATVBA UserForm for text results. VBA compilation, CATIA execution, Forms imports, licensing, and installation remain unverified. CATIA creates the `.catvba` project on the workstation.

## Requirements and source files

Use a Windows workstation with CATIA V5 R32, an available VBA editor with Microsoft Forms, and permission to run macros. Check these permissions and licensing with the workstation administrator. The calculation uses no Excel installation or object model.

- `cad/catia/WrinkleCore.bas` contains the calculation core and uses standard VBA arithmetic and Variant arrays.
- `cad/catia/Launch.bas` opens the form.
- `cad/catia/UserForm-code.txt` contains the text to paste into the form's code window.

Windows CI runs the same calculation core through the standalone CATScript using Windows Script Host. It covers numerical behavior and shared language semantics. VBA project compilation, the Forms designer, and importing into CATIA require local verification. The optional CATVBA workflow uses the installed VBA host.

## 1. Create the CATVBA project

1. Start CATIA and use a blank test part if needed.
2. Open **Tools > Macro > Macros**, select **Macro libraries**, and choose **VBA Projects**. Create or register `WrinkleSourcePreview.catvba` in a local test directory.
3. Open the **Visual Basic Editor** from **Tools > Macro**. Under **File > Import File**, import `WrinkleCore.bas` and `Launch.bas` into the new project. Check that the modules appear as `WrinkleCore` and `Launch`.
4. Select **Insert > UserForm** and set the form's **(Name)** to `frmWrinkle`.

Check the installed CATIA automation help for version-specific editor options. [Import File dialog](https://learn.microsoft.com/en-us/office/vba/language/reference/user-interface-help/import-file-dialog-box) · [Visual Basic Editor File menu](https://learn.microsoft.com/en-us/office/vba/language/reference/user-interface-help/file-menu) · [Dassault Help](https://help.3ds.com/)

## 2. Configure the UserForm

Set the form to approximately **720 × 540 points** and add standard Microsoft Forms controls with the names below. Add labels that identify mm as the input unit.

| Name | Type | Position (Left, Top, Width, Height) and properties |
|---|---|---|
| `txtL1` | TextBox | (180, 15, 100, 22), label `Developed target length l1 [mm]` |
| `txtL2` | TextBox | (180, 45, 100, 22), label `Projected width l2 [mm]` |
| `chkThickness` | CheckBox | (15, 80, 260, 22), caption `Estimate strain from wall thickness` |
| `txtThickness` | TextBox | (180, 110, 100, 22), label `Wall thickness [mm]` |
| `cmdCalculate` | CommandButton | (320, 15, 160, 28), caption `Calculate` |
| `cmdClose` | CommandButton | (500, 15, 120, 28), caption `Close`, Cancel=True |
| `txtResult` | TextBox | (15, 155, 675, 340), MultiLine=True, ScrollBars=3 (Both), WordWrap=False, Locked=True, TabStop=False |

Paste the complete contents of `UserForm-code.txt` into the code window for `frmWrinkle`. Remove any automatically generated empty event procedures that would duplicate the supplied procedures. The UserForm uses `CDbl` and follows the Windows decimal locale. Enter plain numbers without grouping separators.

## 3. Compile, run, and validate

1. In the VBA editor, select **Debug > Compile**. Record compiler errors and check **Tools > References** for missing entries. This project needs no Excel library.
2. Save the project and close the editor. Run `Launch.CATMain` from the macro dialog and confirm that the form appears.
3. With wall thickness on, enter `40 / 30 / 2`. Check A ≈ 6.139413268 mm, R ≈ 5.0322554 mm, height ≈ 12.2342750 mm, angle ≈ 49.8407463°, straight segment length ≈ 11.3319680 mm per side, fitted polyline length ≈ 40.1738373 mm, and analytical fit length ≈ 40.1738725 mm. The length deviation should be **+0.434593%**.
4. Verify the 0.096220 mm RMS and 0.181006 mm maximum vertical shape deviations. Compare the separately labeled strain estimates of 19.871805% for the fitted arcs, 13.465240% for the Excel cosine radius, and 26.930480% for the corrected cosine radius.
5. Try `30 / 30` for a flat result and `80 / 60 / 4` for doubled lengths. Turn the wall thickness checkbox off to check that no strain estimate appears. Check reference cases and tolerances in [the calculation method](MATHEMATICS.md) and [the reference CSV](../reference/cases.csv).
6. Check empty input, text, `29 / 30`, negative thickness with the option on, and `l1 > 2*l2`. Each should produce an error and replace any previous result in the form.
7. Test repeated **Calculate**, **Close**, **Esc**, and reopening. Verify that document geometry and modification status stay unchanged.
8. Save and close CATIA, start it again, and reopen and run the project. Record the CATIA build, Windows version, macro and license configuration, and actual compilation and startup results.

Run `python tools/run_vbscript_tests.py` from the repository root for the independent Windows source check. The result verifies Windows Script Host execution.
