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

    def test_report_compares_cosine_strains_at_a_common_crest_and_keeps_legacy_screening(self):
        import re
        import shutil

        node = shutil.which('node')
        if node is None:
            self.skipTest('Node.js is needed to exercise the browser report')
        journal = runpy.run_path(str(ROOT / 'ready-to-run/NX_WrinkleCalculator.py'))
        template = (ROOT / 'cad/result.html').read_text(encoding='ascii')
        scripts = '\n'.join(re.findall(r'<script(?: id="[a-z-]+")?>(.*?)</script>', template, re.S))
        harness = """
const assert = require('node:assert/strict');
const elements = new Map();
function element(id) {
  if (!elements.has(id)) {
    const paths = [];
    const ctx = {
      beginPath() { this.points = []; },
      moveTo(...p) { this.points.push(p); }, lineTo(...p) { this.points.push(p); },
      stroke() { paths.push(this.points); }, setLineDash() {}, arc() {}, fill() {},
      strokeText() {}, fillText() {}
    };
    elements.set(id, {
      paths, width: 800, height: 250, getContext: () => ctx, value: '', hidden: false,
      classList: {add() {}}, setAttribute() {},
      addEventListener(name, callback) { this[name] = callback; },
      insertRow: () => ({append() {}, insertCell: () => ({})})
    });
  }
  return elements.get(id);
}
const document = {getElementById: element, createElement: () => ({})};
"""
        reference = """
assert.equal(element('legacy-radius').textContent, '7.43 mm');
assert.equal(element('curvature-radius').textContent, '3.71 mm');
assert.equal(element('legacy-strain').textContent, '13.47 %');
assert.equal(element('curvature-strain').textContent, '26.93 %');
const field = element('fracture-elongation');
field.value = '20';
field.input();
assert.match(element('fracture-band').textContent, /^Low/); // 26.93% would give High.
for (const [limit, label] of [['16', /^Critical/], ['12', /^High/]]) {
  field.value = limit;
  field.input();
  assert.match(element('fracture-band').textContent, label);
}
assert.equal(element('crest-plot').hidden, false);
const paths = element('crest-detail').paths.filter(path => path.length > 50);
assert.equal(paths.length, 3, 'the sampled cosine and both circle segments must be drawn');
const [legacy, cosinePath, exact] = paths.sort((a, b) => a[0][1] - b[0][1]);
const center = Math.floor(exact.length / 2);
const [cx, cy] = exact[center];
const radiiInPixels = [];
for (const path of [legacy, exact]) {
  assert.deepEqual(path[center], [cx, cy]);
  const [px, py] = path[0];
  const radius = ((px - cx)**2 + (py - cy)**2) / (2 * (py - cy));
  radiiInPixels.push(radius);
  for (const [x, y] of path) assert.ok(Math.abs(Math.hypot(x - cx, y - cy - radius) - radius) < 1e-8);
}
const pixelsPerMm = radiiInPixels[1] / 3.713264660;
assert.ok(Math.abs(radiiInPixels[0] / pixelsPerMm - 7.426529319) < 1e-7);
assert.deepEqual(cosinePath[center], [cx, cy]);
for (const [x, y] of cosinePath) {
  const dx = (x - cx) / pixelsPerMm;
  const drop = 6.139413271 * (1 - Math.cos(2 * Math.PI * dx / 30));
  assert.ok(Math.abs((y - cy) / pixelsPerMm - drop) < 1e-7);
}
"""
        cases = [
            (40, 30, 2, reference),
            (40, 30, None, r"""
assert.equal(element('legacy-radius').textContent, '7.43 mm');
assert.equal(element('legacy-strain').textContent, '\u2013');
assert.equal(element('curvature-strain').textContent, '\u2013');
assert.equal(element('crest-plot').hidden, false);
assert.match(element('fracture-band').textContent, /^Wall thickness required/);
"""),
            (30, 30, 2, """
assert.match(element('legacy-radius').textContent, /^Unbounded/);
assert.match(element('curvature-radius').textContent, /^Unbounded/);
assert.equal(element('legacy-strain').textContent, '0.00 %');
assert.equal(element('curvature-strain').textContent, '0.00 %');
assert.equal(element('crest-plot').hidden, true);
assert.equal(element('crest-detail').paths.length, 0);
"""),
            (0.002, 0.001, None, """
assert.equal(element('legacy-radius').textContent, '1.22e-4 mm');
assert.equal(element('curvature-radius').textContent, '6.12e-5 mm');
assert.equal(element('crest-plot').hidden, false);
"""),
            (30.000003, 30, 2, """
assert.equal(element('legacy-strain').textContent, '6.62e-3 %');
assert.equal(element('crest-overlap').hidden, false);
assert.ok(element('crest-detail').height < 125, 'nearly flat detail should use only the height it needs');
"""),
        ]
        for l1, l2, thickness, checks in cases:
            with self.subTest(l1=l1, l2=l2, thickness=thickness):
                report = journal['render_illustrated_report'](journal['calculate'](l1, l2, thickness), thickness)
                data = re.search(r'id="result-data" type="application/json">([^<]+)', report)[1]
                inputs = f"element('result-data').textContent = {data!r};\n"
                process = subprocess.run([node, '-'], input=harness + inputs + scripts + '\n{\n' + checks + '}\n',
                                         text=True, capture_output=True, cwd=ROOT)
                self.assertEqual(process.returncode, 0, process.stderr)

if __name__=='__main__': unittest.main()
