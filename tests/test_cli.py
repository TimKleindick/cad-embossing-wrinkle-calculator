import json
import subprocess
import sys
import unittest

class CliTests(unittest.TestCase):
    def test_cli_outputs_numeric_json_and_rejects_invalid_inputs(self):
        p=subprocess.run([sys.executable,'-m','wrinkle','40','30','--thickness','2'],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)
        r=json.loads(p.stdout)
        self.assertAlmostEqual(r['amplitude_mm'],6.139413271,delta=1e-7)
        self.assertGreater(r['length_error_pct'],.4)
        p=subprocess.run([sys.executable,'-m','wrinkle','29','30'],capture_output=True,text=True)
        self.assertNotEqual(p.returncode,0)
        self.assertIn('l2 <= l1',p.stderr)

if __name__=='__main__': unittest.main()
