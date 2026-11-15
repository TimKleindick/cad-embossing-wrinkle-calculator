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
    fields=[('amplitude_mm','A [mm]'),('radius_mm','R [mm]'),('height_mm','Hoehe [mm]'),
            ('phi_deg','Winkel [deg]'),('straight_mm','Gerade je Seite [mm]'),
            ('fit_polygon_mm','Excel-Polygonlaenge [mm]'),('fit_analytic_mm','Analytische Fitlaenge [mm]'),
            ('length_error_pct','Polygon-Laengenabweichung [%]'),
            ('analytic_length_error_pct','Analytische Laengenabweichung [%]'),
            ('rms_form_error_mm','Vertikale Formabweichung RMS [mm]'),
            ('max_form_error_mm','Max. vertikale Formabweichung [mm]'),
            ('cosine_radius_excel_mm','Excel-Kosinusradius [mm]'),
            ('cosine_radius_corrected_mm','Korrigierter Kosinusradius [mm]'),
            ('cosine_strain_excel_pct','Excel-Dehnungsabschaetzung [%]'),
            ('cosine_strain_corrected_pct','Korrigierte Kosinusabschaetzung [%]'),
            ('arc_strain_pct','Kreisbogen-Dehnungsabschaetzung [%]')]
    lines=['SOURCE PREVIEW - CAD-Laufzeit/Import ungetestet','Standard: Excel, 1000 Segmente, Formfit ohne Laengenbedingung']
    for key,label in fields:
        value=result[key]
        lines.append(label+': '+('entfaellt / nicht angegeben' if value is None else format(value,'.9f')))
    if abs(result['length_error_pct']) >= .1:
        lines.append('Laengenziel <0.1% NICHT erreicht; Excel-Standard unveraendert.')
    lines.append('Dehnung: stark vereinfachtes t/(2r)-Modell; keine Materialfreigabe oder Risssicherheitsaussage.')
    return '\n'.join(lines)


class WrinkleDialog:
    def __init__(self):
        self.ui=NXOpen.UI.GetUI()
        path=Path(__file__).with_name('wrinkle.dlx')
        if not path.is_file():
            raise FileNotFoundError('wrinkle.dlx fehlt. In NX Block Styler nach docs/NX2412.md erstellen.')
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
            self.ui.NXMessageBox.Show('Faltenrechner - Source Preview',NXOpen.NXMessageBox.DialogType.Information,text)
            return 0
        except Exception as exc:
            self.ui.NXMessageBox.Show('Faltenrechner',NXOpen.NXMessageBox.DialogType.Error,str(exc))
            return 1


def main():
    instance=None
    try:
        instance=WrinkleDialog()
        instance.dialog.Show()
    except Exception as exc:
        NXOpen.UI.GetUI().NXMessageBox.Show('Faltenrechner - Source Preview',NXOpen.NXMessageBox.DialogType.Error,str(exc))
    finally:
        if instance is not None:
            instance.dialog.Dispose()

if __name__ == '__main__': main()
