"""Windows-only execution of the VBA-compatible pure core, without CATIA."""
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]

def main():
    core = (ROOT / 'cad/catia/WrinkleCore.bas').read_text(encoding='utf-8')
    # Only export metadata is removed; no semantic translation.
    source = '\n'.join(line for line in core.splitlines()
                       if not line.startswith('Attribute ') and line != 'Option Explicit')
    tests = (ROOT / 'cad/catia/test_core.vbs').read_text(encoding='utf-8')
    with tempfile.TemporaryDirectory() as tmp:
        runner = Path(tmp) / 'core_tests.vbs'
        command=['cscript.exe','//nologo',str(runner),str(ROOT/'reference/cases.csv')]
        # Negative control: a silent replacement of the Excel radius must fail.
        mutation=source.replace('rexcel = 1 / (2 * WPI * WPI * a)',
                                'rexcel = 1 / (4 * WPI * WPI * a)')
        if mutation == source:
            raise RuntimeError('negative control mutation no longer applies')
        runner.write_text('Option Explicit\n'+mutation+'\n'+tests,encoding='ascii')
        red=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
        if red.returncode != 1 or 'FAIL: Excel strain' not in red.stdout:
            raise RuntimeError('negative control did not fail as expected: '+red.stdout+red.stderr)
        print('EXPECTED RED: silent Excel radius correction rejected by reference test',flush=True)
        for locale in (1033,1031):
            prefix='Option Explicit\nDim startLocale\nstartLocale = SetLocale('+str(locale)+')\n'
            runner.write_text(prefix+source+'\n'+tests,encoding='ascii')
            print('Testing actual VBA-compatible source with initial locale '+str(locale),flush=True)
            subprocess.run(command,check=True,cwd=ROOT)

if __name__ == '__main__': main()
