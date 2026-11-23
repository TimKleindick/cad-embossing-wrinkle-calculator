# Run the wrinkle calculator in CATIA V5 R32

## What you need

Use **`ready-to-run/CATIA_WrinkleCalculator.CATScript`** on a Windows workstation with CATIA V5 R32, a working VBScript engine, and permission to run macros. The standalone file includes the calculation core, one input form, and the illustrated report. It runs without a CATVBA project, UserForm, Excel installation, or Python. For a designer-built interface, see the [optional UserForm guide](CATIA-V5-R32-UserForm-optional.md).

The input form uses Windows PowerShell and .NET Windows Forms without changing execution policy. If it cannot start, the macro falls back to one CATScript input box. The report uses the Windows default browser and the Windows components `Scripting.FileSystemObject` and `Shell.Application`. If creating or opening the report fails, the macro shows text results. Windows CI checks the macro source and calculation through Windows Script Host and exercises the form outside CATIA. The macro's registration, dialogs, report launch, licensing and installation in CATIA V5 R32 still need workstation verification.

Microsoft lists VBScript as deprecated and available as a Windows Feature on Demand. If the engine is missing or macros are blocked, check the supported CATIA and Windows configuration with IT. [Microsoft VBScript status](https://learn.microsoft.com/en-us/windows/whats-new/deprecated-features-resources)

## 1. Download the macro

1. Open the public [repository on main](https://github.com/TimKleindick/cad-embossing-wrinkle-calculator/tree/main) and choose **Code > Download ZIP**.
2. Save the ZIP locally, for example under `C:\CAD-Test\Wrinkle`. In Windows Explorer, right-click it and select **Extract All**. Open **`ready-to-run`** in the extracted folder.
3. Locate **`CATIA_WrinkleCalculator.CATScript`**. If necessary, enable **View > Show > File name extensions** in Explorer and check that the file ends in `.CATScript`.
4. Alternatively, open the [macro on GitHub](https://github.com/TimKleindick/cad-embossing-wrinkle-calculator/blob/main/ready-to-run/CATIA_WrinkleCalculator.CATScript) and select **Download raw file**. The source starts with `Option Explicit`. For a repeatable workstation test, record the Git commit you downloaded.

A source preview ZIP built with the repository's packaging tool also contains the macro under `ready-to-run`. Keep the original workbook outside the repository and test evidence.

## 2. Register and run the macro

1. Start CATIA V5 R32. If your configuration requires a document to enable the macro menu, open a blank test part.
2. Choose **Tools > Macro > Macros**, then **Macro libraries**.
3. Set **Library type** to **Directories**, choose **Add existing library**, and select the extracted **`ready-to-run`** folder or the local folder where you saved the raw macro. Confirm with **OK**.
4. Select **Close** to return to the macro list. If prompted, select the directory library you just added.
5. Select **`CATIA_WrinkleCalculator`** or the full **`.CATScript`** file name and choose **Run**. CATIA calls `CATMain` and opens a single input window.

Add the directory once and reuse it from the macro dialog. Check whether your R32 configuration retains the library after restart. The menu labels and directory library workflow are documented for older V5 releases. Confirm the exact menu and behavior in your installed version.

## 3. Check the illustrated results

1. Enter `40` for **Undeformed wall length l1** and `30` for **Deformed wall length l2 (neutral fibre)**. The calculator uses `l1` as the target length along the cosine and `l2` as the horizontal span between the endpoints of the deformed neutral-fibre profile.
2. Enter `2` in **Wall thickness**, optionally enter **Elongation at fracture A [%]** (for example `24,5`), and select **Calculate**. Clear the optional thickness field for geometry only. A is a tensile-test reference only, not a cracking limit; it does not change the calculation. Use a decimal point or comma without grouping separators, units, or exponents. If the one-box fallback appears, enter `40;30;2;24,5` or `40;30;;` with both optional values blank.
3. The Windows default browser opens **Wrinkle geometry**, the same offline English report as NX. The sketch labels the three circular arcs with their common radius. The report HTML remains in the Windows temporary directory. If launch fails, the macro shows text results using the Windows number locale.
4. Open **More information** to see the length and shape comparison. The first row shows the entered `l1`. The relative length deviation still compares the fitted polyline with `l1`.

| Quantity | Report value |
|---|---:|
| Undeformed wall length l1 | 40.00 mm |
| Deformed wall length l2 (neutral fibre) | 30.00 mm |
| Circular arc radius R | 5.03 mm |
| Fitted profile height h | 12.23 mm |
| Flank angle φ | 49.84° |
| Analytical length of the fitted profile | 40.17 mm |
| Fitted polyline length deviation from l1 | +0.43% |
| RMS and maximum sampled vertical shape deviations | 0.10 / 0.18 mm |
| Cosine curvature at the crest | 3.71 mm / 26.93% |

In **Cosine bending estimate**, check the minimum cosine radius and estimated outer-fibre bending strain. The text fallback shows the same estimate. The radius is not the fitted circular-arc radius. The simplified bending estimate does not predict cracks or assign a fracture risk band.

## 4. Try cancellation and other inputs

- Select **Cancel** or close the input window to end the run without a report. In the one-box fallback, **Cancel** or submitting a completely blank box also ends the run.
- Clear **Wall thickness** to calculate the cosine radius without a strain estimate. **Elongation at fracture A [%]** is also optional. For the one-box fallback, use `40;30;;` to leave both blank or `40;30;2;24,5` to provide both.
- Try l1 = `29` and l2 = `30`, text in a length field, or negative thickness. The form keeps the fields open and shows an error so you can correct them. With the one-box fallback, dismiss the error and run the macro again. Supported lengths are 0.001 to 1,000,000 mm with `l2 <= l1 <= 2*l2`. Optional wall thickness ranges from 0 to 1,000,000 mm.
- Try l1 = `30` and l2 = `30` with **Wall thickness** blank. The flat profile has no finite cosine radius and, without thickness, no strain value. With thickness entered, the strain estimate is zero.
- Try l1 = `80`, l2 = `60`, and **Wall thickness** = `4`. Absolute lengths double and angles, relative errors, and strain stay the same.
- Verify that CATIA is available after the report opens. Run the macro again and cancel the input window before calculating. Then restart CATIA, check the directory registration, and verify that the macro leaves all geometry and document state unchanged.

## 5. Troubleshoot the workstation

| Observation | Check |
|---|---|
| Macro does not appear | Check that the library type is **Directories** and the selected directory directly contains the extracted `.CATScript` file. Check the file extension. |
| CATIA requests a project or form import | Open the directory macro library and select the standalone file. |
| `ScriptingERR_1002` at `Option Explicit` on line 2 | Replace the older copy in the registered macro directory with the current raw file. `Option Explicit` should be on line 1. |
| Script engine unavailable or policy blocks execution | Give IT the full message, CATIA build, service pack or hotfix, and Windows version. Ask about the supported engine and allowed macro configuration. |
| Input window is hidden | Check the taskbar and **Alt+Tab**. Focus and modality require verification in the CATIA host. |
| Text dialogs appear in place of the profile | Check the Windows default application for HTML and whether CATIA can write to the temporary directory and open that application. |
| Input is rejected | Verify the numeric format, valid ranges, and `l2 <= l1 <= 2*l2`. |
| The strain value is missing | Enter a value in **Wall thickness** in the input window (the third value in the one-box fallback). If you leave it blank, no strain is calculated. |

Record the commit, CATIA build, service pack or hotfix, Windows version, macro permissions, inputs, results, browser launch, cancellation, and restart behavior. Verify that the macro leaves document geometry unchanged.

Dassault's automation conventions place `Option Explicit` first and remove the `Language` assignment from recorded macros. IBM documents the directory library workflow for older V5 releases. The installed CATIA V5 R32 automation help is the version-specific reference. [Dassault CAA macro rules](https://catia-v5-help.anarkia333data.center/online/CAAScrTechArticles/CAAScrScriptCodingRules.htm) · [IBM HE03301](https://www.ibm.com/support/pages/apar/HE03301) · [Dassault Help](https://help.3ds.com/)

The older V5 help also describes opening a `.CATScript` via its Windows file association. Use that path only if the existing association points to the intended R32 installation. The directory library workflow works independently of the file association. [Running a Macro](https://catia-v5-help.anarkia333data.center/online/basug_C2/basugbt1903.htm)
