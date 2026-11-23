"""Exercise the generated CATScript's real Windows form outside CATIA."""
import ctypes
from ctypes import wintypes as w
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
TITLE = 'Wrinkle Geometry - Input'
HARNESS = """
Dim result, status
status = WTryInputForm(result)
WScript.Echo CStr(status) & "|" & CStr(result)
"""


def main():
    if sys.platform != 'win32':
        raise RuntimeError('Windows desktop test requires Windows; CATIA is not loaded')
    user = ctypes.WinDLL('user32', use_last_error=True)
    user.FindWindowW.argtypes = [w.LPCWSTR, w.LPCWSTR]
    user.FindWindowW.restype = w.HWND
    user.GetClassNameW.argtypes = [w.HWND, w.LPWSTR, ctypes.c_int]
    user.GetWindowRect.argtypes = [w.HWND, ctypes.POINTER(w.RECT)]
    callback_type = ctypes.WINFUNCTYPE(w.BOOL, w.HWND, w.LPARAM)
    user.EnumChildWindows.argtypes = [w.HWND, callback_type, w.LPARAM]
    user.SendMessageTimeoutW.argtypes = [
        w.HWND, w.UINT, w.WPARAM, w.LPARAM, w.UINT, w.UINT,
        ctypes.POINTER(ctypes.c_size_t),
    ]
    user.SendMessageTimeoutW.restype = ctypes.c_ssize_t
    user.PostMessageW.argtypes = [w.HWND, w.UINT, w.WPARAM, w.LPARAM]

    def send(hwnd, msg, wp, lp):
        ret = ctypes.c_size_t()
        if not user.SendMessageTimeoutW(hwnd, msg, wp, lp, 3, 5000, ctypes.byref(ret)):
            raise ctypes.WinError(ctypes.get_last_error() or 1460)
        return ret.value

    def controls(window):
        all_controls = []

        @callback_type
        def collect(hwnd, _):
            name = ctypes.create_unicode_buffer(256)
            user.GetClassNameW(hwnd, name, len(name))
            label = ctypes.create_unicode_buffer(512)
            send(hwnd, 0x0D, len(label), ctypes.addressof(label))  # WM_GETTEXT
            rect = w.RECT()
            user.GetWindowRect(hwnd, ctypes.byref(rect))
            all_controls.append((name.value, label.value, rect.top, hwnd))
            return True

        user.EnumChildWindows(window, collect, 0)
        return all_controls

    def wait_for(check, timeout=20):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            hit = check()
            if hit:
                return hit
            time.sleep(0.1)
        raise AssertionError('Timed out waiting for form or feedback')

    source = (ROOT / 'ready-to-run/CATIA_WrinkleCalculator.CATScript').read_text(encoding='ascii')
    with tempfile.TemporaryDirectory() as tmp:
        runner = Path(tmp) / 'form-test.vbs'
        runner.write_text(source + HARNESS, encoding='ascii')
        for cancel in (False, True):
            env = dict(os.environ, TMPDIR=tmp, TEMP=tmp, TMP=tmp)
            process = subprocess.Popen(['cscript.exe', '//nologo', str(runner)], cwd=tmp,
                                       env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       text=True)
            hwnd = None
            try:
                def window():
                    current = user.FindWindowW(None, TITLE)
                    if current and len(controls(current)) >= 14:
                        return current
                    if process.poll() is not None:
                        raise AssertionError(f'Form failed to start: {process.communicate()}')
                    return None

                hwnd = wait_for(window)
                items = controls(hwnd)
                edits = sorted((y, child) for cls, label, y, child in items if '.EDIT.' in cls.upper())
                buttons = {label: child for cls, label, y, child in items if '.BUTTON.' in cls.upper()}
                assert len(edits) == 4, items
                assert any(
                    all(s in label for s in ('L1 = developed', 'L2 = projected', 't = wall thickness',
                                              'A [%] = tensile'))
                    for _, label, _, _ in items
                ), items
                assert 'Calculate' in buttons and 'Cancel' in buttons, items

                if cancel:
                    user.PostMessageW(buttons['Cancel'], 0x00F5, 0, 0)  # BM_CLICK
                    expected = '2|'
                else:
                    def set_text(index, text):
                        data = ctypes.create_unicode_buffer(text)
                        send(edits[index][1], 0x0C, 0, ctypes.addressof(data))  # WM_SETTEXT

                    set_text(0, '29')
                    user.PostMessageW(buttons['Calculate'], 0x00F5, 0, 0)
                    wait_for(lambda: any('Lengths must satisfy' in label
                                         for _, label, _, _ in controls(hwnd)))
                    assert process.poll() is None, 'invalid input closed the dialog'
                    set_text(0, '40,5')
                    set_text(1, '30.25')
                    set_text(2, '')
                    set_text(3, '24,5')
                    user.PostMessageW(buttons['Calculate'], 0x00F5, 0, 0)
                    expected = '0|40,5;30.25;;24,5'
                output, error = process.communicate(timeout=12)
                assert process.returncode == 0 and output.strip() == expected, (output, error)
                assert not list(Path(tmp).glob('Wrinkle-input-*')), 'form left a temporary directory'
            finally:
                if process.poll() is None:
                    if hwnd:
                        user.PostMessageW(hwnd, 0x0010, 0, 0)  # WM_CLOSE
                    try:
                        process.communicate(timeout=4)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.communicate()
    print('PASS: generated CATScript opened one Windows form; validation, locales, cancel, and cleanup. CATIA host UNTESTED.')


if __name__ == '__main__':
    main()
