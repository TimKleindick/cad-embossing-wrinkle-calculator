"""Compile the delivered CATScript and exercise its core in Windows Script Host."""
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]

def main():
    macro = ROOT / 'ready-to-run/CATIA_WrinkleCalculator.CATScript'
    source = macro.read_text(encoding='ascii')
    # Windows Script Host compiles the delivered file without editing its preamble.
    compiled = subprocess.run(
        ['cscript.exe', '//nologo', '//E:VBScript', str(macro)],
        cwd=ROOT, capture_output=True, text=True, timeout=30,
    )
    if compiled.returncode or compiled.stderr.strip() or compiled.stdout.strip():
        raise RuntimeError('Delivered CATScript failed its VBScript compile check:\n'
                           + compiled.stdout + compiled.stderr)
    print('PASS: delivered CATScript compiled with its original preamble', flush=True)
    tests = (ROOT / 'cad/catia/test_core.vbs').read_text(encoding='utf-8')+'\n'+(ROOT/'cad/catia/test_entry.vbs').read_text(encoding='ascii')
    with tempfile.TemporaryDirectory() as tmp:
        runner = Path(tmp) / 'core_tests.vbs'
        command=['cscript.exe','//nologo',str(runner),str(ROOT/'reference/cases.csv')]
        # Negative control: a silent replacement of the Excel radius must fail.
        mutation=source.replace('rexcel = 1 / (2 * WPI * WPI * a)',
                                'rexcel = 1 / (4 * WPI * WPI * a)')
        if mutation == source:
            raise RuntimeError('negative control mutation no longer applies')
        runner.write_text(mutation+'\n'+tests,encoding='ascii')
        red=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
        if red.returncode != 1 or 'FAIL: Excel strain' not in red.stdout:
            raise RuntimeError('negative control did not fail as expected: '+red.stdout+red.stderr)
        print('EXPECTED RED: silent Excel radius correction rejected by reference test',flush=True)
        for locale in (1033,1031):
            locale_setup=f'\nDim startLocale\nstartLocale = SetLocale({locale})\n'
            runner.write_text(source+locale_setup+tests,encoding='ascii')
            print('Testing actual VBA-compatible source with initial locale '+str(locale),flush=True)
            subprocess.run(command,check=True,cwd=ROOT)

if __name__ == '__main__': main()
