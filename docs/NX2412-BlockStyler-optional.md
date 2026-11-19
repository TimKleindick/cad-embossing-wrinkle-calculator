# Optional NX 2412 Block Styler setup

The [standalone journal](NX2412.md) is the standard entry and produces the illustrated report. This optional Windows workstation procedure builds an NX-native Block Styler dialog for text results. NX runtime, the Block Styler import, API compatibility, licensing, and installation remain unverified. Build the `wrinkle.dlx` layout in the installed designer.

## Requirements

Use NX 2412, NX Open Python, and access to Block Styler. Check the bundled Python version in the NX help or by playing a journal containing `import sys; print(sys.version)`. The core uses Python's standard library. The adapter also uses `pathlib` and `NXOpen`. Check designer and journal access with the workstation or license administrator. These sources include neither vendor libraries nor licenses.

## 1. Prepare the files

1. Copy the repository or extract the source preview into a local test folder. Keep the repository structure, including `cad/nx/wrinkle_dialog.py` and `wrinkle/core.py`.
2. Open a blank test part in NX. The numeric inputs use mm regardless of the part units.
3. To check the numerical reference outside NX, run `python -m wrinkle 40 30 --thickness 2`.

## 2. Build the dialog in Block Styler

Open **Block Styler** in the NX command finder. Create a dialog with **OK / Apply / Cancel** and use **Wrinkle Calculator - Source Preview** as its title. Add a group called `inputs` and configure the controls below with the exact IDs. Use plain numbers in mm for these controls.

| Block ID | Type | Label | Initial value |
|---|---|---|---:|
| `l1_mm` | Double | Developed target length l1 [mm] | 40 |
| `l2_mm` | Double | Projected width l2 [mm] | 30 |
| `use_thickness` | Toggle / Check Box with Boolean `Value` | Estimate strain from wall thickness | false |
| `thickness_mm` | Double | Optional wall thickness [mm] | 2 |

Set limits of 0.001 to 1,000,000 mm for the lengths and 0 to 1,000,000 mm for thickness. The calculation core also validates the inputs. Add a note identifying the 1,000-segment Excel method and the fit without a length constraint.

Save the layout as **`cad/nx/wrinkle.dlx`** in the test folder. Generate sample Python code in the designer and compare its calls with the adapter. Check `UI.CreateDialog`, `TopBlock.FindBlock`, the `Double.Value` and Boolean `Value` properties, and the `AddInitializeHandler`, `AddApplyHandler`, and `AddOkHandler` signatures. Record any differences in the installed NX version before running the adapter. The adapter loads the DLX next to the script by its absolute path.

## 3. Play and validate the journal

1. Find **Journal > Play** in NX and select `cad/nx/wrinkle_dialog.py`.
2. Expect the native dialog. If the DLX is missing, expect an error that identifies the missing layout.
3. **Apply** calculates and writes the values to the NX Listing Window and result message. **OK** calculates and closes after a successful callback. **Cancel** closes the dialog.
4. Enter `40 / 30 / 2` with the wall thickness option on. Check A ≈ 6.139413268 mm, R ≈ 5.0322554 mm, height ≈ 12.2342750 mm, angle ≈ 49.8407463°, and straight segment length ≈ 11.3319680 mm per side. The fitted polyline length is approximately 40.1738373 mm and the analytical fit length is approximately 40.1738725 mm.
5. Verify the **+0.434593%** length deviation, the missed 0.1% target, the RMS shape deviation of 0.096220 mm, and the maximum vertical shape deviation of 0.181006 mm. Check that the Excel and corrected cosine strain estimates appear separately.
6. Try `30 / 30` for the flat case, then `80 / 60 / 4` to check scaling. Turn off thickness to check that no strain estimate is reported. Try `29 / 30`, `l1 > 2*l2`, and negative thickness with the option on. Each invalid input should produce an error.
7. Test repeated **Apply**, **OK**, **Cancel**, and reopening. Record your NX and Windows builds, Python version, layout and licensing checks, inputs and results. Verify that part geometry and document state remain unchanged. Distribute a native DLX only after validating it in the target NX version.

Consult the NX 2412 help under **NX Open Python Reference / Block UI Styler** for your installation. [Siemens Support](https://support.sw.siemens.com/)
