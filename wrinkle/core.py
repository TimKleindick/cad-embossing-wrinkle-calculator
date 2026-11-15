"""Excel-compatible calculation; no CAD, spreadsheet, or optimizer dependency.

All fitting uses dimensionless coordinates. The fitted length is a diagnostic,
never a constraint. See docs/MATHEMATICS.md for the precise sampling contract.
"""
import math

PI = math.pi


def _number(value, name, minimum, maximum):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(name + ' must be a finite number')
    if not math.isfinite(value) or not minimum <= value <= maximum:
        raise ValueError(name + ' outside supported source-preview range')


def _segments(n):
    if isinstance(n, bool) or not isinstance(n, int) or n < 100 or n > 20000 or n % 2:
        raise ValueError('segments must be an even integer from 100 to 20000')


def cosine_polygon(amplitude, l2, segments=1000):
    """Length of exactly N chords at x=i*l2/N (not the analytic arc)."""
    _number(amplitude, 'amplitude', 0, 1e6)
    _number(l2, 'l2', .001, 1e6)
    _segments(segments)
    a = amplitude / l2
    old = 0.0
    total = 0.0
    for i in range(1, segments + 1):
        y = 2 * a * math.sin(PI * i / segments) ** 2
        total += math.hypot(1 / segments, y - old)
        old = y
    return total * l2


def _amplitude(ratio, n):
    factors = [2 * math.sin(PI * i / n) ** 2 for i in range(n + 1)]
    differences = [factors[i] - factors[i-1] for i in range(1, n+1)]
    low, high = 0.0, ratio / 4
    for _ in range(64):
        a = (low + high) / 2
        length = sum(math.hypot(1 / n, a * dy) for dy in differences)
        if length < ratio:
            low = a
        else:
            high = a
    return (low + high) / 2


def _parameters(q, phi):
    radius = q / (4 * math.sin(phi))
    first = q / 4
    second = .5 - first
    height = .5 * (1-q) * math.tan(phi) + .5 * q * math.tan(phi/2)
    return radius, first, second, height


def _ordinate(u, radius, first, second, height, slope, start_y):
    # Rationalized circle sag avoids catastrophic subtraction near the flat case.
    if u < first:
        return u*u / (radius + math.sqrt(max(0.0, radius*radius-u*u)))
    if u <= second:
        return start_y + (u-first)*slope
    d = .5-u
    return height - d*d / (radius + math.sqrt(max(0.0, radius*radius-d*d)))


def profile_y(x, l2, radius, phi):
    """Symmetric three-circle/two-tangent graph; phi in radians."""
    _number(l2, 'l2', .001, 1e6)
    _number(x, 'x', 0, l2)
    _number(radius, 'radius', 1e-100, 1e100)
    _number(phi, 'phi', 1e-100, PI/2-1e-6)
    q = 4 * radius / l2 * math.sin(phi)
    if q > 1:
        raise ValueError('negative tangent length')
    r, first, second, h = _parameters(q, phi)
    u = min(x, l2-x)/l2
    start_y = 2*r*math.sin(phi/2)**2
    return l2 * _ordinate(u, r, first, second, h, math.tan(phi), start_y)


def _simplex(objective, q):
    vertices = [[q,1.0],[q+.05,1.0],[q,1.1]]
    scores = [objective(v) for v in vertices]
    for iteration in range(400):
        order = sorted(range(3), key=lambda i: scores[i])
        vertices, scores = [vertices[i] for i in order], [scores[i] for i in order]
        if max(abs(vertices[i][j]-vertices[0][j]) for i in (1,2) for j in (0,1)) < 1e-9:
            return vertices[0], scores[0], iteration
        center = [(vertices[0][j]+vertices[1][j])/2 for j in (0,1)]
        reflected = [2*center[j]-vertices[2][j] for j in (0,1)]
        fr = objective(reflected)
        if fr < scores[0]:
            expanded = [center[j]+2*(reflected[j]-center[j]) for j in (0,1)]
            fe = objective(expanded)
            vertices[2],scores[2] = (expanded,fe) if fe < fr else (reflected,fr)
        elif fr < scores[1]:
            vertices[2],scores[2] = reflected,fr
        else:
            outside = fr < scores[2]
            target = reflected if outside else vertices[2]
            contracted = [(center[j]+target[j])/2 for j in (0,1)]
            fc = objective(contracted)
            if fc < (fr if outside else scores[2]):
                vertices[2],scores[2] = contracted,fc
            else:
                for i in (1,2):
                    vertices[i] = [(vertices[0][j]+vertices[i][j])/2 for j in (0,1)]
                    scores[i] = objective(vertices[i])
    raise ArithmeticError('form fit did not converge; no result released')


def calculate(l1, l2, thickness=None, segments=1000):
    """Return mm/degree/% diagnostics for 1 <= l1/l2 <= 2.

    Exact flat input is supported. Optional thickness is used only for the very
    simplified t/(2r) strain estimate; no material or crack-safety conclusion.
    """
    _number(l1, 'l1', .001, 1e6)
    _number(l2, 'l2', .001, 1e6)
    if not l2 <= l1 <= 2*l2:
        raise ValueError('source preview requires l2 <= l1 <= 2*l2')
    if thickness is not None:
        _number(thickness, 'thickness', 0, 1e6)
    _segments(segments)
    result = dict(segments=segments, l1_mm=l1, l2_mm=l2)
    if l1 == l2:
        result.update(amplitude_mm=0., radius_mm=None, height_mm=0., phi_deg=0.,
                      straight_mm=l2/2, fit_polygon_mm=l2, fit_analytic_mm=l2,
                      length_error_pct=0., analytic_length_error_pct=0.,
                      rms_form_error_mm=0., max_form_error_mm=0., vertical_sse_mm2=0.,
                      cosine_radius_excel_mm=None, cosine_radius_corrected_mm=None,
                      iterations=0)
        for k in ('arc_strain_pct','cosine_strain_excel_pct','cosine_strain_corrected_pct'):
            result[k] = None if thickness is None else 0.
        return result
    a = _amplitude(l1/l2,segments)
    base_phi = math.atan(2*PI*a)
    us = [i/segments for i in range(segments//2+1)]
    ys = [2*a*math.sin(PI*u)**2 for u in us]
    weights = [2.] * len(us)
    weights[-1] = 1.

    def objective(v):
        q, phi = v[0], v[1]*base_phi
        if not 1e-8 < q < 1-1e-8 or not 0 < phi < PI/2-1e-6:
            return 1e100
        r, first, second, h = _parameters(q,phi)
        slope, start_y = math.tan(phi), 2*r*math.sin(phi/2)**2
        return sum(w*(_ordinate(u,r,first,second,h,slope,start_y)-y)**2
                   for u,y,w in zip(us,ys,weights))

    candidates = [_simplex(objective,q) for q in (.3,.7)]
    best, score, iterations = min(candidates,key=lambda c:c[1])
    q,phi = best[0],best[1]*base_phi
    if q < 1e-6 or q > 1-1e-6:
        raise ArithmeticError('degenerate fit boundary; no result released')
    r, first, second, h = _parameters(q,phi)
    s = (.5-2*r*math.sin(phi))/math.cos(phi)
    sampled = [_ordinate(u,r,first,second,h,math.tan(phi),2*r*math.sin(phi/2)**2) for u in us]
    polygon = 2*sum(math.hypot(1/segments,sampled[i]-sampled[i-1]) for i in range(1,len(us)))
    analytic = 4*r*phi+2*s
    rexcel = 1/(2*PI*PI*a)
    rcorrected = rexcel/2
    result.update(amplitude_mm=a*l2, radius_mm=r*l2, height_mm=h*l2,
                  phi_deg=phi*180/PI, straight_mm=s*l2,
                  fit_polygon_mm=polygon*l2, fit_analytic_mm=analytic*l2,
                  length_error_pct=(polygon*l2/l1-1)*100,
                  analytic_length_error_pct=(analytic*l2/l1-1)*100,
                  rms_form_error_mm=math.sqrt(score/(segments+1))*l2,
                  max_form_error_mm=max(abs(y-z) for y,z in zip(ys,sampled))*l2,
                  vertical_sse_mm2=score*l2*l2, iterations=iterations,
                  cosine_radius_excel_mm=rexcel*l2, cosine_radius_corrected_mm=rcorrected*l2)
    for key, radius in [('arc_strain_pct',r),('cosine_strain_excel_pct',rexcel),('cosine_strain_corrected_pct',rcorrected)]:
        result[key] = None if thickness is None else 100*(thickness/l2)/(2*radius)
    return result
