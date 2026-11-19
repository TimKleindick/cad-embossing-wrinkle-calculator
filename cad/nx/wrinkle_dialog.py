"""NX 2412 source preview. Requires a locally built wrinkle.dlx; CAD UNTESTED.

This adapter reads native blocks and displays numbers. It creates no geometry.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from wrinkle.core import calculate
import NXOpen
import NXOpen.BlockStyler


def report(result):
    fields=[('amplitude_mm','A [mm]'),('radius_mm','R [mm]'),('height_mm','Height h [mm]'),
            ('phi_deg','Flank angle [deg]'),('straight_mm','Straight length per side [mm]'),
            ('fit_polygon_mm','Fitted polyline length [mm]'),('fit_analytic_mm','Analytic fitted length [mm]'),
            ('length_error_pct','Polyline length deviation [%]'),
            ('analytic_length_error_pct','Analytic length deviation [%]'),
            ('rms_form_error_mm','RMS vertical profile deviation [mm]'),
            ('max_form_error_mm','Maximum vertical deviation at sample points [mm]'),
            ('cosine_radius_excel_mm','Cosine radius using the Excel formula [mm]'),
            ('cosine_radius_corrected_mm','Corrected cosine radius [mm]'),
            ('cosine_strain_excel_pct','Cosine strain using the Excel radius [%]'),
            ('cosine_strain_corrected_pct','Cosine strain using the corrected radius [%]'),
            ('arc_strain_pct','Circular arc strain estimate [%]')]
    lines=['SOURCE PREVIEW - CAD runtime and import untested','Excel method with 1,000 segments and no fitted-length constraint']
    for key,label in fields:
        value=result[key]
        lines.append(label+': '+('Not applicable or not provided' if value is None else format(value,'.9f')))
    if abs(result['length_error_pct']) >= .1:
        lines.append('Length deviation reaches or exceeds 0.1%.')
    lines.append('Simplified t/(2r) estimate. Material approval and crack safety are outside its scope.')
    return '\n'.join(lines)


class WrinkleDialog:
    def __init__(self):
        self.ui=NXOpen.UI.GetUI()
        path=Path(__file__).with_name('wrinkle.dlx')
        if not path.is_file():
            raise FileNotFoundError('wrinkle.dlx is missing. Create it using the optional Block Styler guide.')
        self.dialog=self.ui.CreateDialog(str(path))
        self.dialog.AddInitializeHandler(self.initialize)
        self.dialog.AddApplyHandler(self.apply)
        self.dialog.AddOkHandler(self.apply)

    def initialize(self):
        top=self.dialog.TopBlock
        self.l1=top.FindBlock('l1_mm')
        self.l2=top.FindBlock('l2_mm')
        self.thickness=top.FindBlock('thickness_mm')
        self.use_thickness=top.FindBlock('use_thickness')
        self.l1.Value=40.
        self.l2.Value=30.
        self.thickness.Value=2.
        self.use_thickness.Value=False

    def apply(self):
        try:
            thickness=self.thickness.Value if self.use_thickness.Value else None
            text=report(calculate(self.l1.Value,self.l2.Value,thickness))
            listing=NXOpen.Session.GetSession().ListingWindow
            listing.Open()
            listing.WriteLine(text)
            self.ui.NXMessageBox.Show('Wrinkle Geometry - Source Preview',NXOpen.NXMessageBox.DialogType.Information,text)
            return 0
        except Exception as exc:
            self.ui.NXMessageBox.Show('Wrinkle Geometry',NXOpen.NXMessageBox.DialogType.Error,str(exc))
            return 1


def main():
    instance=None
    try:
        instance=WrinkleDialog()
        instance.dialog.Show()
    except Exception as exc:
        NXOpen.UI.GetUI().NXMessageBox.Show('Wrinkle Geometry - Source Preview',NXOpen.NXMessageBox.DialogType.Error,str(exc))
    finally:
        if instance is not None:
            instance.dialog.Dispose()

if __name__ == '__main__': main()
