"""Windows dialog adapter for an inlined NX Python journal; NX integration untested.

The generator places the unchanged pure core before this adapter. Only Windows
system DLLs are loaded, at run time. No NX object, file, or geometry is modified.
"""
import re
import struct
import sys

WINDOW_TITLE = 'Faltenrechner - Source Preview - CAD ungetestet'


def parse_decimal(text):
    text=text.strip()
    if len(text)>32 or not re.fullmatch(r'[+-]?[0-9]+(?:[.,][0-9]+)?',text):
        raise ValueError('Zahl mit Punkt oder Komma eingeben; keine Tausendertrennzeichen/Exponenten.')
    return float(text.replace(',','.'))


def format_report(result):
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
    lines=['Excel: 1000 Segmente; Formfit ohne Laengenbedingung.']
    for key,label in fields:
        value=result[key]
        lines.append(label+': '+('entfaellt / nicht angegeben' if value is None else format(value,'.9f')))
    if abs(result['length_error_pct'])>=.1:
        lines.append('Laengenziel <0.1% NICHT erreicht; Excel-Standard unveraendert.')
    lines.append('Dehnung: stark vereinfachtes t/(2r)-Modell; keine Materialfreigabe oder Risssicherheitsaussage.')
    return '\r\n'.join(lines)


def dialog_template():
    """Standard DLGTEMPLATE + 11 actual controls; DWORD aligned as Win32 requires."""
    def wide(text): return (text+'\0').encode('utf-16-le')
    style=0x80000000|0x00c00000|0x00080000|0x40|0x80|0x800
    data=struct.pack('<IIHhhhh',style,0,11,0,0,468,332)
    data+=b'\0\0\0\0'+wide(WINDOW_TITLE)+struct.pack('<H',9)+wide('Segoe UI')
    child=0x50000000
    tab=0x10000
    # id, standard control class atom, text, x,y,w,h, style, extended style
    controls=[
        (10001,0x82,'Abgewickelte Laenge l1 [mm]',12,12,150,14,0,0),
        (101,0x81,'40',174,10,95,16,tab|0x80,0x200),
        (10002,0x82,'Projizierte Breite l2 [mm]',12,36,150,14,0,0),
        (102,0x81,'30',174,34,95,16,tab|0x80,0x200),
        (104,0x80,'Dickenabschaetzung aktivieren',12,60,250,14,tab|3,0),
        (10003,0x82,'Wanddicke [mm]',12,84,150,14,0,0),
        (103,0x81,'2',174,82,95,16,tab|0x80,0x200),
        (1,0x80,'Berechnen',304,10,68,20,tab|1,0),
        (2,0x80,'Schliessen',382,10,72,20,tab,0),
        (10004,0x82,'SOURCE PREVIEW - NX-Laufzeit/Installation ungetestet',12,110,440,14,0,0),
        (201,0x81,'Berechnen zeigt Ergebnisse. Punkt oder Komma als Dezimaltrenner.',12,132,442,186,
         tab|0x4|0x40|0x800|0x200000|0x100000|0x80,0x200),
    ]
    for ident,atom,text,x,y,w,h,flags,extended in controls:
        data+=b'\0'*((-len(data))%4)
        data+=struct.pack('<IIhhhhH',child|flags,extended,x,y,w,h,ident)
        data+=struct.pack('<HH',0xffff,atom)+wide(text)+b'\0\0'
    return data


def run_dialog(owner=None):
    if sys.platform!='win32':
        raise RuntimeError('Dieser vorbereitete NX-Einstieg benoetigt Windows und Python ctypes.')
    import ctypes
    from ctypes import wintypes as w
    user=ctypes.WinDLL('user32',use_last_error=True)
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    callback_type=ctypes.WINFUNCTYPE(ctypes.c_ssize_t,w.HWND,w.UINT,w.WPARAM,w.LPARAM)
    # Explicit pointer-sized types prevent HWND/callback truncation in 64-bit NX.
    user.DialogBoxIndirectParamW.argtypes=[w.HINSTANCE,ctypes.c_void_p,w.HWND,callback_type,w.LPARAM]
    user.DialogBoxIndirectParamW.restype=ctypes.c_ssize_t
    user.EndDialog.argtypes=[w.HWND,ctypes.c_ssize_t];user.EndDialog.restype=w.BOOL
    user.GetDlgItemTextW.argtypes=[w.HWND,ctypes.c_int,w.LPWSTR,ctypes.c_int]
    user.GetDlgItemTextW.restype=w.UINT
    user.SetDlgItemTextW.argtypes=[w.HWND,ctypes.c_int,w.LPCWSTR];user.SetDlgItemTextW.restype=w.BOOL
    user.IsDlgButtonChecked.argtypes=[w.HWND,ctypes.c_int];user.IsDlgButtonChecked.restype=w.UINT
    user.GetForegroundWindow.restype=w.HWND
    kernel.GetModuleHandleW.argtypes=[w.LPCWSTR];kernel.GetModuleHandleW.restype=w.HMODULE
    failures=[]

    def read(hwnd,ident):
        text=ctypes.create_unicode_buffer(256)
        user.GetDlgItemTextW(hwnd,ident,text,len(text))
        return parse_decimal(text.value)

    @callback_type
    def callback(hwnd,message,wp,lp):
        try:
            if message==0x110:  # WM_INITDIALOG
                return 1
            if message==0x10 or (message==0x111 and (wp&0xffff)==2):
                user.EndDialog(hwnd,1)
                return 1
            if message==0x111 and (wp&0xffff)==1:  # IDOK: calculate, keep dialog open
                try:
                    thickness=read(hwnd,103) if user.IsDlgButtonChecked(hwnd,104)==1 else None
                    text=format_report(calculate(read(hwnd,101),read(hwnd,102),thickness))
                except (ValueError,ArithmeticError) as exc:
                    text='Fehler: '+str(exc)+'\r\nKein Ergebnis freigegeben.'
                user.SetDlgItemTextW(hwnd,201,text)
                return 1
            return 0
        except Exception as exc:
            # Never let a Python exception escape through a native callback.
            failures.append(str(exc))
            user.EndDialog(hwnd,1)
            return 1

    template=ctypes.create_string_buffer(dialog_template())
    if owner is None: owner=user.GetForegroundWindow()
    value=user.DialogBoxIndirectParamW(kernel.GetModuleHandleW(None),template,owner,callback,0)
    if value in (-1,0): raise ctypes.WinError(ctypes.get_last_error())
    if failures: raise RuntimeError('Dialogfehler: '+failures[0])


if __name__=='__main__':
    run_dialog()
