import importlib.util
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]

def adapter():
    spec=importlib.util.spec_from_file_location('entry_dialog',ROOT/'cad/nx/win32_dialog.py')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class EntryTests(unittest.TestCase):
    def test_decimal_inputs_are_unambiguous_across_locales(self):
        ui=adapter()
        for text,want in [('40',40),(' 6,25 ',6.25),('6.25',6.25),('-2',-2),('+0.5',.5)]:
            self.assertEqual(ui.parse_decimal(text),want)
        for text in ['', ' ', '1,234.5','1.234,5','1 000','1e3','nan','inf','.5','1.','--1','2mm']:
            with self.subTest(text=text),self.assertRaises(ValueError): ui.parse_decimal(text)

    def test_dialog_template_has_real_inputs_and_result_controls(self):
        ui=adapter()
        data=ui.dialog_template()
        import struct
        self.assertGreater(len(data),300)
        self.assertEqual(struct.unpack_from('<H',data,8)[0],11)
        for label in ['Undeformed wall length l1 [mm]', 'Deformed wall length l2 (neutral fibre) [mm]', 'Calculate', 'Close']:
            self.assertIn(label.encode('utf-16-le'),data)

    def test_generated_nx_journal_is_standalone_and_matches_reference(self):
        source=ROOT/'ready-to-run/NX_WrinkleCalculator.py'
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/source.name
            target.write_bytes(source.read_bytes())
            command='import runpy,json; m=runpy.run_path("NX_WrinkleCalculator.py"); print(json.dumps(m["calculate"](40,30,2)))'
            p=subprocess.run([sys.executable,'-I','-c',command],cwd=tmp,capture_output=True,text=True,check=True)
            import json
            r=json.loads(p.stdout)
            self.assertAlmostEqual(r['amplitude_mm'],6.139413271,delta=1e-7)
            self.assertGreater(r['length_error_pct'],.4)

    def test_catscript_emits_option_explicit_before_any_statement(self):
        from tools.build_entries import generated_sources

        path = 'ready-to-run/CATIA_WrinkleCalculator.CATScript'
        source = generated_sources(ROOT)[path].decode('ascii')
        self.assertEqual(source.splitlines()[0], 'Option Explicit')
        self.assertNotRegex(source, r'(?im)^\s*Language\s*=')
        self.assertEqual((ROOT / path).read_bytes(), source.encode('ascii'))

    def test_standalone_catscript_contains_the_complete_result_template(self):
        from tools.build_entries import generated_sources

        path = 'ready-to-run/CATIA_WrinkleCalculator.CATScript'
        script = generated_sources(ROOT)[path].decode('ascii')
        template = (ROOT / 'cad/result.html').read_text(encoding='ascii')
        _, found, body = script.partition('Function WResultTemplate()\n')
        self.assertTrue(found, 'standalone macro is missing its report template')
        statements = body.partition('End Function')[0].splitlines()
        prefix = '    html = html & "'
        suffix = '" & vbLf'
        embedded = [line[len(prefix):-len(suffix)].replace('""', '"')
                    for line in statements if line.startswith(prefix) and line.endswith(suffix)]
        self.assertEqual('\n'.join(embedded) + '\n', template)
        self.assertEqual((ROOT / path).read_bytes(), script.encode('ascii'))

    def test_standalone_nx_uses_the_same_english_report_and_real_profile(self):
        import json
        import re

        path = ROOT / 'ready-to-run/NX_WrinkleCalculator.py'
        with tempfile.TemporaryDirectory() as tmp:
            journal = Path(tmp) / path.name
            journal.write_bytes(path.read_bytes())
            source = runpy.run_path(str(journal))
            self.assertEqual(source['REPORT_TEMPLATE'],
                             (ROOT / 'cad/result.html').read_text(encoding='ascii'))
            for l1, thickness in [(40, 2), (30, None)]:
                with self.subTest(l1=l1):
                    result = source['calculate'](l1, 30, thickness)
                    html = source['render_illustrated_report'](result, thickness)
                    self.assertIn('<html lang="en">', html)
                    payload = re.search(r'id="result-data" type="application/json">([^<]+)', html)
                    data = json.loads(payload.group(1))
                    self.assertEqual((data['l1'], data['l2'], data['thickness']), (l1, 30, thickness))
                    self.assertEqual(len(data['fit']), 201)
                    self.assertEqual(data['fit'][0], 0)
                    self.assertEqual(data['fit'][-1], 0)
                    self.assertAlmostEqual(data['fit'][100], result['height_mm'], places=10)
                    self.assertEqual(data['values'][1], result['radius_mm'])

    def test_report_screens_unrounded_strain_at_both_thresholds(self):
        import re
        import shutil

        node = shutil.which('node')
        if node is None:
            self.skipTest('Node.js is needed to exercise the shared browser rules')
        template = (ROOT / 'cad/result.html').read_text(encoding='ascii')
        script = re.search(r'<script id="screening-rules">(.*?)</script>', template, re.S)
        self.assertIsNotNone(script, 'report needs shared screening rules')
        checks = """
const assert = require('node:assert/strict');
for (const [strain, elongation, expected] of [
  [6.999, 10, 'low'], [7, 10, 'critical'], [9.999, 10, 'critical'],
  [10, 10, 'high'], [13.4652400467, 13.47, 'critical'], [0, 10, 'low'],
  [null, 10, null], [1, null, null], [1, 0, null], [1, -2, null],
]) assert.equal(fractureBand(strain, elongation), expected);
assert.equal(parseFractureElongation('13,47'), 13.47);
assert.equal(parseFractureElongation('13.47'), 13.47);
for (const value of ['', '0', '-5', '1,000.00', 'Infinity', '15%'])
  assert.equal(parseFractureElongation(value), null);
"""
        subprocess.run([node, '-e', script.group(1) + checks], check=True, cwd=ROOT)

    def test_generation_check_rejects_stale_delivery(self):
        from tools.build_entries import generated_sources,check_generated
        expected=generated_sources(ROOT)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for name,data in expected.items():
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
            check_generated(root,expected)
            p=root/'ready-to-run/NX_WrinkleCalculator.py';p.write_bytes(p.read_bytes()+b'\n# stale')
            with self.assertRaises(ValueError): check_generated(root,expected)

if __name__=='__main__': unittest.main()
