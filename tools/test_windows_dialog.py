"""Exercise the actual generated Windows dialog in a separate process, outside NX."""
import ctypes
from ctypes import wintypes as w
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]


def main():
    if sys.platform!='win32':
        raise RuntimeError('Windows desktop test requires Windows; NX is not loaded')
    user=ctypes.WinDLL('user32',use_last_error=True)
    user.FindWindowW.argtypes=[w.LPCWSTR,w.LPCWSTR];user.FindWindowW.restype=w.HWND
    user.GetWindowThreadProcessId.argtypes=[w.HWND,ctypes.POINTER(w.DWORD)]
    user.GetDlgItem.argtypes=[w.HWND,ctypes.c_int];user.GetDlgItem.restype=w.HWND
    user.SendMessageTimeoutW.argtypes=[w.HWND,w.UINT,w.WPARAM,w.LPARAM,w.UINT,w.UINT,ctypes.POINTER(ctypes.c_size_t)]
    user.SendMessageTimeoutW.restype=ctypes.c_ssize_t
    def send(hwnd,message,wp=0,lp=0):
        result=ctypes.c_size_t()
        ctypes.set_last_error(0)
        if not user.SendMessageTimeoutW(hwnd,message,wp,lp,3,5000,ctypes.byref(result)):
            raise ctypes.WinError(ctypes.get_last_error() or 1460)
        return result.value
    def set_text(hwnd,ident,value):
        data=ctypes.create_unicode_buffer(value)
        send(user.GetDlgItem(hwnd,ident),0x0c,0,ctypes.addressof(data))  # WM_SETTEXT
    title='Faltenrechner - Source Preview - CAD ungetestet'
    with tempfile.TemporaryDirectory() as tmp:
        file=Path(tmp)/'NX_WrinkleCalculator.py'
        shutil.copyfile(ROOT/'ready-to-run/NX_WrinkleCalculator.py',file)
        process=subprocess.Popen([sys.executable,'-I',str(file)],cwd=tmp,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        hwnd=None
        try:
            deadline=time.monotonic()+15
            while time.monotonic()<deadline:
                candidate=user.FindWindowW(None,title)
                pid=w.DWORD()
                if candidate:
                    user.GetWindowThreadProcessId(candidate,ctypes.byref(pid))
                    if pid.value==process.pid:
                        hwnd=candidate
                        break
                if process.poll() is not None:
                    out,err=process.communicate()
                    raise AssertionError('entry exited before showing real dialog: '+out+err)
                time.sleep(.05)
            if hwnd is None: raise AssertionError('real Windows dialog not created')
            def text():
                buf=ctypes.create_unicode_buffer(8192)
                send(user.GetDlgItem(hwnd,201),0x0d,len(buf),ctypes.addressof(buf))  # WM_GETTEXT
                return buf.value
            def click():
                send(user.GetDlgItem(hwnd,1),0xf5)  # BM_CLICK
            set_text(hwnd,101,'40')
            set_text(hwnd,102,'30')
            set_text(hwnd,103,'2')
            send(user.GetDlgItem(hwnd,104),0xf1,1)
            click()
            report=text()
            assert '6.139413268' in report,report
            assert '40.173837' in report and 'NICHT erreicht' in report,report
            assert '13.465240' in report and '26.930480' in report,report
            # German decimal is accepted independently of machine locale.
            set_text(hwnd,101,'40,0');click()
            assert '6.139413268' in text(),text()
            # Invalid input replaces the previous successful report.
            set_text(hwnd,101,'29');click()
            assert text().startswith('Fehler:') and '6.139413268' not in text(),text()
            # Flat input and disabled thickness ignore an invalid inactive field.
            set_text(hwnd,101,'30')
            set_text(hwnd,103,'disabled text')
            send(user.GetDlgItem(hwnd,104),0xf1,0);click()
            assert 'entfaellt / nicht angegeben' in text() and 'Fehler:' not in text(),text()
            send(hwnd,0x10)  # WM_CLOSE
            out,err=process.communicate(timeout=10)
            assert process.returncode==0,out+err
            print('PASS: actual Win32 dialog from isolated single file; calculation, comma input, invalid/flat input and close. NX host UNTESTED.')
        finally:
            if process.poll() is None:
                if hwnd:
                    try: send(hwnd,0x10)
                    except OSError: pass
                try: process.communicate(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill();process.communicate()

if __name__=='__main__': main()
