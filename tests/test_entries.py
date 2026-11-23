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
        self.assertEqual(struct.unpack_from('<H',data,8)[0],13)
        for label in ['Undeformed wall length l1 [mm]', 'Deformed wall length l2 (neutral fibre) [mm]', 'Elongation at fracture A [%] (optional)', 'Calculate', 'Close']:
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

    def test_catscript_embeds_one_local_form_and_a_one_box_fallback(self):
        from tools.build_entries import generated_sources

        script = generated_sources(ROOT)['ready-to-run/CATIA_WrinkleCalculator.CATScript'].decode('ascii')
        self.assertIn('Function WInputFormScript()', script)
        self.assertIn('Add-Type -AssemblyName System.Windows.Forms', script)
        self.assertIn('Undeformed wall length l1 [mm]', script)
        self.assertIn('Deformed wall length l2 (neutral fibre) [mm]', script)
        self.assertIn('Wall thickness [mm]', script)
        self.assertIn('Elongation at fracture A [%] (optional)', script)
        self.assertNotIn('ConfirmThickness', script)
        self.assertEqual(script.lower().count('inputbox('), 1)
        self.assertIn('-NoProfile -NonInteractive -STA -File', script)
        self.assertNotRegex(script, r'(?i)-executionpolicy|-encodedcommand|mshta')

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

    def test_sketch_draws_cosine_dimension_and_distinct_fitted_flanks(self):
        import re
        import shutil

        node = shutil.which('node')
        if node is None:
            self.skipTest('Node.js is needed to exercise the shared sketch')
        journal = runpy.run_path(str(ROOT / 'ready-to-run/NX_WrinkleCalculator.py'))
        template = (ROOT / 'cad/result.html').read_text(encoding='ascii')
        sketch = 'const canvas = ' + template.split('const canvas = ', 1)[1].split('</script>', 1)[0]
        harness = r"""
const assert = require('node:assert/strict');
const strokes = [], labels = [];
const context = {
  beginPath() { this.points = []; },
  moveTo(...point) { this.points.push(point); },
  lineTo(...point) { this.points.push(point); },
  setLineDash(dash) { this.dash = dash; },
  stroke() { strokes.push({points: this.points, color: this.strokeStyle, width: this.lineWidth, dash: this.dash}); },
  arc() {}, strokeText() {}, fillText(text) { labels.push(text); }
};
const drawingSurface = {width: 1000, height: 350, getContext: () => context};
const document = {getElementById: id => id === 'profile' ? drawingSurface : {}};
const withUnit = (value, unit) => `${value.toFixed(2)} ${unit}`;
const near = (first, second) => Math.abs(first - second) < 1e-7;
const samePoint = (first, second) => first.every((n, i) => near(n, second[i]));
"""
        reference = 'const reference = strokes.find(stroke => stroke.dash.length && stroke.points.length > 100);\n'
        dimension = r"""
const measure = strokes.find(stroke => stroke.color === reference.color &&
  !stroke.dash.length && stroke.points.length === reference.points.length);
assert.ok(measure, 'l1 needs a separate endpoint-to-endpoint cosine stroke');
const gap = reference.points[0][1] - measure.points[0][1];
assert.ok(gap > 10 && measure.points.every(([px, py], i) =>
  near(px, reference.points[i][0]) && near(py + gap, reference.points[i][1])));
for (const i of [0, measure.points.length - 1]) {
  const point = measure.points[i];
  const markers = strokes.filter(stroke => stroke.color === measure.color && stroke.points.length === 2 &&
    samePoint(stroke.points[0], point));
  assert.ok(markers.length >= 2, 'both l1 endpoints need arrowheads');
}
assert.ok(labels.includes(`l\u2081 = ${withUnit(l1, 'mm')}`));
const [leftX, baseline] = reference.points[0];
const [rightX] = reference.points.at(-1);
assert.ok(strokes.some(({points}) => points.length === 2 && near(points[0][0], leftX) &&
  near(points[1][0], rightX) && near(points[0][1], points[1][1]) && points[0][1] > baseline));
"""
        flanks = """
const fitStrokes = strokes.filter(stroke => stroke.width >= 3 && !stroke.dash.length);
const arcs = fitStrokes.filter(stroke => stroke.points.length > 2);
const straights = fitStrokes.filter(stroke => stroke.points.length === 2);
assert.equal(arcs.length, radius === null ? 0 : 3, 'draw each circular arc on the fitted profile');
assert.equal(straights.length, radius === null ? 1 : 2, 'draw both fitted straight segments');
if (radius !== null) {
  assert.ok(arcs.every(stroke => stroke.color === arcs[0].color));
  assert.ok(straights.every(stroke => stroke.color === straights[0].color && stroke.color !== arcs[0].color));
  assert.ok(arcs[0].color !== reference.color && straights[0].color !== reference.color);
  for (let i = 0; i < straights.length; i++) {
    assert.ok(samePoint(straights[i].points[0], arcs[i].points.at(-1)));
    assert.ok(samePoint(straights[i].points[1], arcs[i + 1].points[0]));
  }
}
"""
        for l1 in (40, 30):
            report = journal['render_illustrated_report'](journal['calculate'](l1, 30, 2), 2)
            data = re.search(r'id="result-data" type="application/json">([^<]+)', report).group(1)
            inputs = f'const {{l1, l2, values, fit}} = {data}; const [amplitude, radius, height, angle] = values;\n'
            for feature, checks in [('cosine dimension', dimension), ('fitted profile', flanks)]:
                with self.subTest(l1=l1, feature=feature):
                    process = subprocess.run([node, '-'], input=harness + inputs + sketch + '{\n' + reference + checks + '}\n',
                                             text=True, capture_output=True, cwd=ROOT)
                    self.assertEqual(process.returncode, 0, process.stderr)

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

    def test_elongation_at_fracture_is_optional_reference_not_geometry(self):
        import json
        import re

        source = runpy.run_path(str(ROOT / 'ready-to-run/NX_WrinkleCalculator.py'))
        value = source['parse_elongation_at_fracture'](' 24,5 ')
        self.assertEqual(value, 24.5)
        self.assertIsNone(source['parse_elongation_at_fracture'](' '))
        with self.assertRaises(ValueError):
            source['parse_elongation_at_fracture']('-1')
        result = source['calculate'](40, 30, 2)
        usual = source['format_report'](result, 2)
        reference = source['format_report'](result, 2, value)
        self.assertNotIn('Elongation at fracture A', usual)
        self.assertIn('Elongation at fracture A: 24.50 %', reference)
        self.assertIn('not a cracking limit', reference)
        self.assertIn('outer-fibre strain = 26.93 %', reference)
        def read_payload(html):
            return json.loads(re.search(r'id="result-data" type="application/json">([^<]+)', html).group(1))
        without = read_payload(source['render_illustrated_report'](result, 2))
        with_reference = read_payload(source['render_illustrated_report'](result, 2, value))
        self.assertEqual(with_reference.pop('elongationAtFracture'), 24.5)
        self.assertEqual(with_reference, without)

    def test_standalone_nx_text_shows_only_cosine_curvature_estimate(self):
        source = runpy.run_path(str(ROOT / 'ready-to-run/NX_WrinkleCalculator.py'))
        for lengths, thickness, radius, strain in [
            ((40, 30), 2, '3.71 mm', '26.93 %'),
            ((40, 30), None, '3.71 mm', 'not calculated (no thickness)'),
            ((30, 30), 2, 'unbounded (flat cosine)', '0.00 %'),
            ((0.002, 0.001), 0.000000001, '6.12e-5 mm', '8.17e-4 %'),
        ]:
            with self.subTest(lengths=lengths, thickness=thickness):
                result = source['calculate'](*lengths, thickness)
                lines = source['format_report'](result, thickness).splitlines()
                self.assertIn(f'Cosine curvature: R = {radius}, outer-fibre strain = {strain}', lines)
                self.assertEqual(sum('outer-fibre strain =' in line for line in lines), 1)
                self.assertNotIn('legacy', ' '.join(lines).lower())
                self.assertIn('not a crack prediction', ' '.join(lines).lower())

    def test_report_shows_only_cosine_curvature_without_zoom_or_fracture_badge(self):
        import re
        import shutil

        journal = runpy.run_path(str(ROOT / 'ready-to-run/NX_WrinkleCalculator.py'))
        report = journal['render_illustrated_report'](journal['calculate'](40, 30, 2), 2)
        self.assertEqual(re.findall(r'<canvas\b[^>]*\bid="([^"]+)"', report), ['profile'])
        self.assertIn('<summary>More information</summary>', report)
        self.assertNotRegex(report, r'(?i)legacy estimate|fracture-band|fracture-elongation')
        self.assertIn('not a crack prediction', report.lower())

        node = shutil.which('node')
        if node is None:
            self.skipTest('Node.js is needed to exercise the browser report values')
        harness = """
const assert = require('node:assert/strict');
const elements = new Map();
const context = new Proxy({}, {get: (object, name) => object[name] || (() => {})});
for (const id of reportIds) {
  elements.set(id, {
    width: 1000, height: 350, getContext: () => context, hidden: false,
    classList: {add() {}}, insertRow: () => ({append() {}, insertCell: () => ({})})
  });
}
const document = {getElementById: id => elements.get(id), createElement: () => ({})};
elements.get('result-data').textContent = JSON.stringify(data);
"""
        checks = """
assert.equal(elements.get('curvature-radius').textContent, expectedRadius);
assert.equal(elements.get('curvature-strain').textContent, expectedStrain);
assert.equal(elements.get('wall-thickness').textContent, expectedThickness);
assert.ok(elements.get('length-target').textContent.includes('0.10%'));
"""
        import json
        for l1, l2, thickness, radius, strain, wall in [
            (40, 30, 2, '3.71 mm', '26.93 %', '2.00 mm'),
            (40, 30, None, '3.71 mm', '\u2013', '\u2013'),
            (30, 30, 2, 'Unbounded (flat cosine)', '0.00 %', '2.00 mm'),
            (30, 30, None, 'Unbounded (flat cosine)', '\u2013', '\u2013'),
            (.002, .001, .000000001, '6.12e-5 mm', '8.17e-4 %', '0.00 mm'),
            (30.000003, 30, 2, '7549.37 mm', '0.01 %', '2.00 mm'),
        ]:
            with self.subTest(l1=l1, l2=l2, thickness=thickness):
                result = journal['calculate'](l1, l2, thickness)
                html = journal['render_illustrated_report'](result, thickness)
                ids = re.findall(r'\bid="([^"]+)"', html)
                data = re.search(r'id="result-data" type="application/json">([^<]+)', html)[1]
                js = '\n'.join(re.findall(r'<script(?: id="[a-z-]+")?>(.*?)</script>', html, re.S))
                inputs = f'const reportIds = {json.dumps(ids)}, data = {data};\n'
                expected = list(map(json.dumps, (radius, strain, wall)))
                expectations = f'const [expectedRadius, expectedStrain, expectedThickness] = [{", ".join(expected)}];\n'
                process = subprocess.run([node, '-'], input=inputs + harness + js + '\n' + expectations + checks,
                                         text=True, capture_output=True, cwd=ROOT)
                self.assertEqual(process.returncode, 0, process.stderr)

if __name__=='__main__': unittest.main()
