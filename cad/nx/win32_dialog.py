"""Windows dialog adapter for an inlined NX Python journal; NX integration untested.

The generator places the pure core and shared report template before this adapter.
The journal creates a local HTML report. It does not modify any NX documents.
"""
import json
from math import radians
import os
import re
import struct
import sys
import tempfile

WINDOW_TITLE = 'Wrinkle Geometry - Source Preview'


def parse_decimal(text):
    text=text.strip()
    if len(text)>32 or not re.fullmatch(r'[+-]?[0-9]+(?:[.,][0-9]+)?',text):
        raise ValueError('Enter a number with a decimal point or comma. Do not use digit grouping or exponents.')
    return float(text.replace(',','.'))


def parse_elongation_at_fracture(text):
    """Report-only percentage; blank does not change the geometry or strain."""
    if not text.strip():
        return None
    value = parse_decimal(text)
    if value < 0 or value > 1_000_000:
        raise ValueError('Elongation at fracture A must be between 0 and 1000000 %.')
    return value


def _cosine_number(value, unit):
    if 0 < value < .01:
        mantissa, exponent = f'{value:.2e}'.split('e')
        return f'{mantissa}e{int(exponent)} {unit}'
    return f'{value:.2f} {unit}'


def format_report(result, thickness=None, fracture_elongation=None):
    fields = (
        ('Undeformed wall length l1 [mm]', result['l1_mm']),
        ('Deformed wall length l2 (neutral fibre) [mm]', result['l2_mm']),
        ('Circular arc radius R [mm]', result['radius_mm']),
        ('Height h [mm]', result['height_mm']),
        ('Flank angle [deg]', result['phi_deg']),
        ('Wall thickness [mm]', thickness),
    )
    lines = [
        f'{label}: {value:.2f}' if value is not None else f'{label}: Not applicable or not provided'
        for label, value in fields
    ]
    lines.append('l2 is the horizontal endpoint span of the neutral fibre.')
    radius = result['cosine_radius_corrected_mm']
    strain = result['cosine_strain_corrected_pct']
    radius_text = 'unbounded (flat cosine)' if radius is None else _cosine_number(radius, 'mm')
    strain_text = 'not calculated (no thickness)' if strain is None else _cosine_number(strain, '%')
    lines.append(f'Cosine curvature: R = {radius_text}, outer-fibre strain = {strain_text}')
    if fracture_elongation is not None:
        lines.append(f'Elongation at fracture A: {fracture_elongation:.2f} % (reference; not a cracking limit)')
    lines.append('The cosine bending estimate is not a crack prediction or material approval.')
    return '\r\n'.join(lines)


def render_illustrated_report(result, thickness, fracture_elongation=None):
    """Use the result-data schema shared with the CATScript launcher."""
    fields = (
        'amplitude_mm', 'radius_mm', 'height_mm', 'phi_deg', 'straight_mm',
        'fit_polygon_mm', 'fit_analytic_mm', 'length_error_pct',
        'rms_form_error_mm', 'max_form_error_mm', 'cosine_radius_excel_mm',
        'cosine_radius_corrected_mm', 'arc_strain_pct', 'cosine_strain_excel_pct',
        'cosine_strain_corrected_pct', 'vertical_sse_mm2', 'segments',
    )
    span = result['l2_mm']
    radius = result['radius_mm']
    phi = radians(result['phi_deg'])
    if radius is None:
        fit = [0] * 201
    else:
        fit = [profile_y(span * (i / 200), span, radius, phi) for i in range(201)]
    data = {
        'l1': result['l1_mm'], 'l2': span, 'thickness': thickness,
        'values': [result[field] for field in fields], 'fit': fit,
    }
    if fracture_elongation is not None:
        data['elongationAtFracture'] = fracture_elongation
    return REPORT_TEMPLATE.replace('{{DATA}}', json.dumps(data, allow_nan=False))


def open_illustrated_report(result, thickness, opener=None, *, fracture_elongation=None):
    open_file = opener if opener is not None else getattr(os, 'startfile', None)
    if open_file is None:
        raise OSError('No Windows file opener is available.')
    with tempfile.NamedTemporaryFile(mode='w', encoding='ascii', prefix='Wrinkle-geometry-',
                                     suffix='.html', delete=False) as report:
        report.write(render_illustrated_report(result, thickness, fracture_elongation))
    open_file(report.name)


def dialog_template():
    """Standard DLGTEMPLATE + 13 actual controls; DWORD aligned as Win32 requires."""
    def wide(text): return (text+'\0').encode('utf-16-le')
    style=0x80000000|0x00c00000|0x00080000|0x40|0x80|0x800
    data=struct.pack('<IIHhhhh',style,0,13,0,0,468,356)
    data+=b'\0\0\0\0'+wide(WINDOW_TITLE)+struct.pack('<H',9)+wide('Segoe UI')
    child=0x50000000
    tab=0x10000
    # id, standard control class atom, text, x,y,w,h, style, extended style
    controls=[
        (10001,0x82,'Undeformed wall length l1 [mm]',12,12,187,14,0,0),
        (101,0x81,'40',204,10,90,16,tab|0x80,0x200),
        (10002,0x82,'Deformed wall length l2 (neutral fibre) [mm]',12,36,187,14,0,0),
        (102,0x81,'30',204,34,90,16,tab|0x80,0x200),
        (104,0x80,'Estimate strain from wall thickness',12,60,250,14,tab|3,0),
        (10003,0x82,'Wall thickness [mm]',12,84,187,14,0,0),
        (103,0x81,'2',204,82,90,16,tab|0x80,0x200),
        (10005,0x82,'Elongation at fracture A [%] (optional)',12,108,187,14,0,0),
        (105,0x81,'',204,106,90,16,tab|0x80,0x200),
        (1,0x80,'Calculate',304,10,68,20,tab|1,0),
        (2,0x80,'Close',382,10,72,20,tab,0),
        (10004,0x82,'SOURCE PREVIEW - NX runtime and installation untested',12,134,440,14,0,0),
        (201,0x81,'Calculate opens the illustrated report. Use a decimal point or comma.',12,156,442,186,
         tab|0x4|0x40|0x800|0x200000|0x100000|0x80,0x200),
    ]
    for ident,atom,text,x,y,w,h,flags,extended in controls:
        data+=b'\0'*((-len(data))%4)
        data+=struct.pack('<IIhhhhH',child|flags,extended,x,y,w,h,ident)
        data+=struct.pack('<HH',0xffff,atom)+wide(text)+b'\0\0'
    return data


def run_dialog(owner=None, open_file=None):
    if sys.platform!='win32':
        raise RuntimeError('This NX journal requires Windows and Python ctypes.')
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

    def read_text(hwnd,ident):
        text=ctypes.create_unicode_buffer(256)
        user.GetDlgItemTextW(hwnd,ident,text,len(text))
        return text.value

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
                    thickness=parse_decimal(read_text(hwnd,103)) if user.IsDlgButtonChecked(hwnd,104)==1 else None
                    fracture_elongation = parse_elongation_at_fracture(read_text(hwnd,105))
                    result=calculate(parse_decimal(read_text(hwnd,101)),parse_decimal(read_text(hwnd,102)),thickness)
                except (ValueError,ArithmeticError) as exc:
                    text='Error: '+str(exc)+'\r\nNo result.'
                else:
                    text=format_report(result, thickness, fracture_elongation)
                    try:
                        open_illustrated_report(result, thickness, opener=open_file,
                                                fracture_elongation=fracture_elongation)
                    except (OSError, NotImplementedError):
                        text+='\r\nCould not open the illustrated report. Results are shown above.'
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
    if failures: raise RuntimeError('Dialog error: '+failures[0])


if __name__=='__main__':
    run_dialog()
