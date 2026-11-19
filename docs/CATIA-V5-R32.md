# Run the wrinkle calculator in CATIA V5 R32

## What you need

Use **`ready-to-run/CATIA_WrinkleCalculator.CATScript`** on a Windows workstation with CATIA V5 R32, a working VBScript engine, and permission to run macros. The standalone file includes the calculation core, native input prompts, and the illustrated report. It runs without a CATVBA project, UserForm, Excel installation, or Python. For a designer-built interface, see the [optional UserForm guide](CATIA-V5-R32-UserForm-optional.md).

The report uses the Windows default browser and the Windows components `Scripting.FileSystemObject` and `Shell.Application`. If creating or opening the report fails, the macro shows text results. Windows CI checks the macro source and calculation through Windows Script Host. The macro's registration, dialogs, report launch, licensing and installation in CATIA V5 R32 still need workstation verification.

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
5. Select **`CATIA_WrinkleCalculator`** or the full **`.CATScript`** file name and choose **Run**. CATIA calls `CATMain` and opens the first input box for `l1`.

Add the directory once and reuse it from the macro dialog. Check whether your R32 configuration retains the library after restart. The menu labels and directory library workflow are documented for older V5 releases. Confirm the exact menu and behavior in your installed version.

## 3. Check the illustrated results

1. Enter `40` for **Undeformed wall length l1** and `30` for **Deformed wall length l2 (neutral fibre)**. The calculator uses `l1` as the target length along the cosine and `l2` as the horizontal span between the endpoints of the deformed neutral-fibre profile.
2. Choose **Yes** at **Estimate strain from wall thickness?**, enter `2` for the wall thickness, and confirm. All lengths are in mm. Use a decimal point or comma, with no grouping separators, units, or exponents.
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
| Calculated outer-fibre strain | 13.47% |

In **Strain and fracture screening**, enter fracture elongation A (%) from an applicable tensile test or DIN EN 755-2. Verify the alloy, temper and product dimensions before choosing the value. For this reference case, `20` gives the low band, `16` the critical band and `12` the high band. The report compares the full-precision strain with 70% and 100% of the entered value. The two-decimal display does not affect the assessment. The bands are a screening rule and cannot establish whether cracking will occur. [DIN EN 755-2:2025](https://www.dinmedia.de/en/standard/din-en-755-2/393018811)

## 4. Try cancellation and other inputs

- **Cancel** or an empty value ends the run before calculation. CATIA's input box reports a blank confirmation and a cancellation the same way.
- **No** at the wall thickness prompt calculates without strain estimates. **Cancel** ends the run. **Yes** requires a wall thickness value.
- Try `29 / 30`, text in a length field, or negative thickness. The calculator should show an error without a success report. Supported lengths are 0.001 to 1,000,000 mm with `l2 <= l1 <= 2*l2`. Optional wall thickness ranges from 0 to 1,000,000 mm.
- Try `30 / 30` with thickness off. The profile is flat, with zero height, angle and deviations. The circular arc radius and the strain estimate are unavailable.
- Try `80 / 60 / 4`. Absolute lengths double and angles, relative errors and strain estimates stay the same.
- Verify that CATIA is available after the report opens. Run the macro again and cancel after the first input. Then restart CATIA, check the directory registration, and verify that the macro leaves all geometry and document state unchanged.

## 5. Troubleshoot the workstation

| Observation | Check |
|---|---|
| Macro does not appear | Check that the library type is **Directories** and the selected directory directly contains the extracted `.CATScript` file. Check the file extension. |
| CATIA requests a project or form import | Open the directory macro library and select the standalone file. |
| `ScriptingERR_1002` at `Option Explicit` on line 2 | Replace the older copy in the registered macro directory with the current raw file. `Option Explicit` should be on line 1. |
| Script engine unavailable or policy blocks execution | Give IT the full message, CATIA build, service pack or hotfix, and Windows version. Ask about the supported engine and allowed macro configuration. |
| Input box is hidden | Check the taskbar and **Alt+Tab**. Focus and modality require verification in the CATIA host. |
| Text dialogs appear in place of the profile | Check the Windows default application for HTML and whether CATIA can write to the temporary directory and open that application. |
| Input is rejected | Verify the numeric format, valid ranges, and `l2 <= l1 <= 2*l2`. |
| Strain values are missing | Choose **Yes** at the wall thickness prompt and enter a value. **No** leaves the estimates blank. |

Record the commit, CATIA build, service pack or hotfix, Windows version, macro permissions, inputs, results, browser launch, cancellation, and restart behavior. Verify that the macro leaves document geometry unchanged.

Dassault's automation conventions place `Option Explicit` first and remove the `Language` assignment from recorded macros. IBM documents the directory library workflow for older V5 releases. The installed CATIA V5 R32 automation help is the version-specific reference. [Dassault CAA macro rules](https://catia-v5-help.anarkia333data.center/online/CAAScrTechArticles/CAAScrScriptCodingRules.htm) · [IBM HE03301](https://www.ibm.com/support/pages/apar/HE03301) · [Dassault Help](https://help.3ds.com/)

The older V5 help also describes opening a `.CATScript` via its Windows file association. Use that path only if the existing association points to the intended R32 installation. The directory library workflow works independently of the file association. [Running a Macro](https://catia-v5-help.anarkia333data.center/online/basug_C2/basugbt1903.htm)
