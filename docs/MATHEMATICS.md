# Calculation contract

All lengths are in millimeters. The solvers use radians internally and report angles in degrees. One symmetric period has projected width `l2` and target cosine polyline length `l1`.

## 1. Excel-compatible cosine reference

The reference profile is `y(x)=A*(1-cos(2*pi*x/l2))`. The solver finds `A >= 0` by 64 bisection steps so the sum of the 1000 chord lengths between points `x_i=i*l2/1000`, for `i=0..1000`, equals `l1`. The calculation uses the dimensionless amplitude `a=A/l2` and requires no external solver. The upper bisection bound is `a=(l1/l2)/4`, since the total vertical variation is `4*a`.

The target applies to the sampled polyline. In the reference case, that length is 40 mm, while independent Simpson integration gives a continuous cosine length of 40.000027699761 mm.

## 2. Three equal radii and two tangents

The three arcs have angles `phi, 2*phi, phi`. Each straight segment has length

`s=(l2/2-2*R*sin(phi))/cos(phi)`.

The profile height is `h=(l2/2-2*R*sin(phi))*tan(phi)+2*R*(1-cos(phi))`.

The analytical length is `4*R*phi+2*s`. The profile is tangent at all four joins. Curvature changes discontinuously where each straight segment meets an arc.

For a numerically stable evaluation, define `u=min(x,l2-x)/l2`, `rho=R/l2`, `q=4*rho*sin(phi)`, `u1=q/4`, `u2=1/2-q/4`, and `H=h/l2`. The normalized ordinate `Y` is defined piecewise.

- For `u < u1`, use `Y=u²/(rho+sqrt(rho²-u²))`.
- For `u1 <= u <= u2`, use `Y=2*rho*sin(phi/2)²+(u-u1)*tan(phi)`.
- For `u > u2`, use `Y=H-(1/2-u)²/(rho+sqrt(rho²-(1/2-u)²))`.

Here `H=(1-q)*tan(phi)/2+q*tan(phi/2)/2` and `y=l2*Y`. The rationalized circle formulas avoid cancellation near the flat solution.

## 3. Shape fit without a length constraint

The objective is `sum((y_fit(x_i)-y_cos(x_i))²)` at the same 1001 x positions. Symmetry reduces this to 501 evaluations, with weights of two except at the peak. The fit uses vertical residuals and solves for positive radii and straight segments over `0<q<1` and `0<phi<pi/2`.

Two deterministic Nelder-Mead runs start at `q=0.3,0.7` and `z=1`, with `phi=z*atan(2*pi*a)`. Their initial simplex steps are 0.05 and 0.1. Each run terminates when the simplex span is less than `1e-9`, with a limit of 400 iterations per start. Failure to converge or a degenerate boundary solution raises an error. An independent nested golden-section search confirms the reference case. Global optimality across the whole input range remains unproven.

The fitted polyline length uses exactly 1000 x intervals. The analytical length is reported separately. Both lengths are compared with `l1`, and a positive error means the fitted profile is longer than the target. Peak height and vertical residuals describe the fitted profile. RMS is `sqrt(SSE/1001)`. The reported maximum is the greatest absolute vertical residual at the sample positions.

## 4. Flat limit and supported range

For exactly `l1=l2`, `A=h=phi=0`, both straight segments have length `l2/2`, the fitted length is `l2`, and the error is zero. Arc and cosine radii are undefined (Python `None`, VBA `Empty`). The simplified strain estimate is zero when thickness is supplied and omitted when thickness is absent.

The validated range is `0.001 <= l1,l2 <= 1e6`, `l2 <= l1 <= 2*l2`, and optional thickness from 0 to `1e6`. Boolean values, nonnumeric types, NaN, and infinity are invalid. The Python diagnostic `segments` option accepts even integers from 100 through 20000. **The default and both CAD interfaces use 1000 segments.** Higher counts change the Excel sampling convention and are provided to study convergence. The VBA entry uses a fixed segment count.

## 5. Radius and simplified strain

For `y(x)=a*(1-cos(2*pi*x/l2))`, `a` is half the full cosine height and is the amplitude `A` from section 2. The crest is at `x=l2/2`, where `y'=0` and `|y''|=4*pi²*a/l2²`. This is a maximum of `|y''|/(1+y'^2)^(3/2)`, so the local minimum radius is `l2²/(4*pi²*a)`, shown as **Cosine curvature**. The workbook's `check cracks` worksheet uses `l2²/(2*pi²*a)`, shown as **Legacy estimate**. The crest detail draws both circle segments on the same scale, tangent to the sampled cosine at the crest. The smaller circle matches its local curvature. The legacy circle has twice the radius and shares the tangency.

Optional strain in percent is `100*t/(2*r)`. This simplified estimate omits flow curves, neutral-axis shifts, tool friction, thickness changes, prior plastic deformation, and multiaxial stresses. Crack risk, manufacturability, and approval require separate assessment.

The illustrated CAD report displays both cosine estimates. Fracture screening compares the unrounded **Legacy estimate** strain with the manually entered fracture elongation A (%). The report screens below 70% of that value as low, from 70% to below 100% as critical, and at or above 100% as high. These thresholds are a user-defined screening rule. DIN EN 755-2 specifies mechanical properties for aluminium extrusions. The input must come from an applicable tensile test or a value for the applicable product dimensions, alloy and temper. [DIN EN 755-2:2025](https://www.dinmedia.de/en/standard/din-en-755-2/393018811)

## 6. Result fields and common references

`reference/cases.csv` contains the supplied 40/30/2 case, the flat 30/30/2 case, and homogeneous scaling to 80/60/4. The reference numbers came from the supplied case description. Dimensional fit tolerance is `1e-6 mm * (l2/30)` and angle tolerance is `1e-5` degrees. Solver history and rounded reference values limit the comparison to numerical tolerances. Observed differences for the reference case are considerably smaller.

The VBA function `WrinkleCalculate(l1,l2,thickness)` returns a zero-based Variant array.

| Index | Python field | Unit |
|---:|---|---|
| 0 | amplitude_mm | mm |
| 1 | radius_mm | mm / Empty |
| 2 | height_mm | mm |
| 3 | phi_deg | degrees |
| 4 | straight_mm | mm per side |
| 5 | fit_polygon_mm | mm |
| 6 | fit_analytic_mm | mm |
| 7 | length_error_pct | % relative to l1 |
| 8 | rms_form_error_mm | mm |
| 9 | max_form_error_mm | mm at sample positions |
| 10 | cosine_radius_excel_mm | mm / Empty |
| 11 | cosine_radius_corrected_mm | mm / Empty |
| 12 | arc_strain_pct | % / Empty |
| 13 | cosine_strain_excel_pct | % / Empty |
| 14 | cosine_strain_corrected_pct | % / Empty |
| 15 | vertical_sse_mm2 | mm² |
| 16 | segments | 1000 |

Python additionally returns `analytic_length_error_pct`, the input lengths, and the iteration count for the selected run. `thickness=None` or VBA `Empty` omits strain estimates. A thickness of zero explicitly requests an estimate at zero thickness.
