"""Each test catches a changed numerical contract, not source layout."""
import csv
import math
import pathlib
import unittest
from wrinkle.core import calculate, profile_y, cosine_polygon

ROOT = pathlib.Path(__file__).resolve().parents[1]

class CoreTests(unittest.TestCase):
    def test_supplied_excel_results_and_non_length_preserving_default(self):
        with (ROOT / 'reference/cases.csv').open() as f:
            cases = list(csv.DictReader(f))
        for c in cases:
            with self.subTest(c['id']):
                r = calculate(float(c['l1_mm']), float(c['l2_mm']), float(c['t_mm']))
                for key in ('amplitude_mm','radius_mm','height_mm','phi_deg','straight_mm','fit_polygon_mm','fit_analytic_mm'):
                    if c[key] == '':
                        self.assertIsNone(r[key])
                    else:
                        # Excel Solver stopping differs from a converged minimizer.
                        tol = (1e-5 if key == 'phi_deg' else 1e-6 * float(c['l2_mm']) / 30)
                        self.assertAlmostEqual(r[key], float(c[key]), delta=tol)
        r = calculate(40,30,2)
        self.assertEqual(r['segments'],1000)
        self.assertGreater(r['length_error_pct'],0.4)
        self.assertLess(r['length_error_pct'],0.5)
        self.assertGreater(r['max_form_error_mm'],0)
        self.assertGreater(r['rms_form_error_mm'],0)

    def test_cosine_polygon_is_not_replaced_by_analytic_arc(self):
        self.assertAlmostEqual(cosine_polygon(6.139413271,30),40,delta=2e-8)
        self.assertGreater(cosine_polygon(6.139413271,30,10000),40.00002)

    def test_flat_limit_has_no_artificial_finite_radius(self):
        r=calculate(30,30,2)
        self.assertEqual(r['height_mm'],0)
        self.assertIsNone(r['radius_mm'])
        self.assertIsNone(r['cosine_radius_excel_mm'])
        self.assertEqual(r['arc_strain_pct'],0)
        self.assertEqual(r['length_error_pct'],0)

    def test_invalid_and_unsupported_inputs(self):
        for args in [(29,30,None),(0,0,None),(-1,1,None),(40,float('nan'),None),
                     (float('inf'),30,None),(40,30,-1),(40,30,float('inf')),
                     (61,30,None),(40,0.0001,None),(1e7,1e7,None),(True,1,None)]:
            with self.subTest(args),self.assertRaises(ValueError): calculate(*args)
        for n in [0,999,1001,True,20002,1000.0]:
            with self.subTest(n=n),self.assertRaises(ValueError): calculate(40,30,segments=n)

    def test_scaling_preserves_shape_and_dimensionless_metrics(self):
        a,b=calculate(40,30,2),calculate(400,300,20)
        for k in ['amplitude_mm','radius_mm','height_mm','straight_mm','max_form_error_mm','rms_form_error_mm']:
            self.assertAlmostEqual(b[k],10*a[k],delta=1e-8)
        for k in ['phi_deg','length_error_pct','arc_strain_pct']:
            self.assertAlmostEqual(a[k],b[k],delta=1e-9)

    def test_radius_conventions_are_separate_and_strains_are_not_approval(self):
        r=calculate(40,30,2)
        self.assertAlmostEqual(r['cosine_radius_excel_mm'],2*r['cosine_radius_corrected_mm'],delta=1e-10)
        self.assertAlmostEqual(r['cosine_strain_excel_pct'],13.465,delta=.001)
        self.assertAlmostEqual(r['cosine_strain_corrected_pct'],26.93,delta=.002)
        self.assertAlmostEqual(r['arc_strain_pct'],19.87,delta=.01)
        self.assertIsNone(calculate(40,30)['arc_strain_pct'])

    def test_joins_symmetry_endpoints_and_tangency(self):
        r=calculate(40,30)
        rad,phi=r['radius_mm'],math.radians(r['phi_deg'])
        a=rad*math.sin(phi)
        for x in [0,a,15-a,15,15+a,30-a,30]:
            self.assertAlmostEqual(profile_y(x,30,rad,phi),profile_y(30-x,30,rad,phi),delta=1e-12)
        self.assertAlmostEqual(profile_y(0,30,rad,phi),0,delta=1e-12)
        self.assertAlmostEqual(profile_y(15,30,rad,phi),r['height_mm'],delta=1e-10)
        eps=1e-5
        for x in [a,15-a]:
            y=profile_y(x,30,rad,phi)
            left=(y-profile_y(x-eps,30,rad,phi))/eps
            right=(profile_y(x+eps,30,rad,phi)-y)/eps
            self.assertAlmostEqual(left,math.tan(phi),delta=1e-5)
            self.assertAlmostEqual(right,left,delta=1e-5)
        self.assertAlmostEqual((profile_y(eps,30,rad,phi)-profile_y(0,30,rad,phi))/eps,0,delta=2e-6)
        with self.assertRaises(ValueError): profile_y(-1,30,rad,phi)

    def test_grid_convergence_without_changing_default(self):
        a,b,c=[calculate(40,30,segments=n) for n in (500,1000,2000)]
        self.assertLess(abs(c['amplitude_mm']-b['amplitude_mm']),abs(b['amplitude_mm']-a['amplitude_mm']))
        self.assertLess(abs(c['fit_analytic_mm']-b['fit_analytic_mm']),.0002)
        self.assertLess(c['fit_polygon_mm'],c['fit_analytic_mm'])

    def test_near_flat_and_envelope_end_are_finite(self):
        for l1 in [30.00003,60]:
            r=calculate(l1,30)
            self.assertTrue(all(math.isfinite(v) for v in r.values() if isinstance(v,float)))
            self.assertAlmostEqual(cosine_polygon(r['amplitude_mm'],30),l1,delta=1e-8)
            self.assertGreater(r['straight_mm'],0)

if __name__=='__main__': unittest.main()
