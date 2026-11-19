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
        for label in ['Abgewickelte Laenge l1 [mm]','Berechnen','Schliessen']:
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
