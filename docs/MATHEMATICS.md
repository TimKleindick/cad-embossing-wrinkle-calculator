# Rechenvertrag

Alle Längen in mm, Winkel intern im Bogenmaß, Ausgabe in Grad. Eine symmetrische Periode hat die projizierte Breite `l2`, die gewünschte Kosinus-Polygonlänge ist `l1`.

## 1. Kosinus: Excel-Semantik

`y(x)=A*(1-cos(2*pi*x/l2))`. Für `x_i=i*l2/1000`, `i=0..1000`, wird die Summe der 1000 Sehnenlängen durch Bisektion von `A >= 0` auf `l1` eingestellt. 64 Bisektionsschritte, dimensionslose Rechnung mit `a=A/l2`; keine Solver-Laufzeitabhängigkeit. Der obere Bisektionswert `a=(l1/l2)/4` begrenzt die Lösung, da die gesamte vertikale Variation `4*a` beträgt.

Die analytische Kosinuslänge wird **nicht** zur Lösung benutzt. Beim Standardfall ist die Kosinus-Polygonlänge 40 mm, die durch unabhängige Simpson-Integration ermittelte kontinuierliche Kosinuslänge 40,000027699761 mm.

## 2. Drei gleiche Radien und zwei Tangenten

Die drei Bögen haben Winkel `phi, 2*phi, phi`; beide Geraden haben Länge

`s=(l2/2-2*R*sin(phi))/cos(phi)`.

`h=(l2/2-2*R*sin(phi))*tan(phi)+2*R*(1-cos(phi))`.

Die analytische Länge ist `4*R*phi+2*s`. Das Profil ist an den vier Übergängen tangential; seine Krümmung springt an den Geradenübergängen.

Für die robuste Berechnung: `u=min(x,l2-x)/l2`, `rho=R/l2`, `q=4*rho*sin(phi)`, `u1=q/4`, `u2=1/2-q/4`, `H=h/l2`:

- `u < u1`: `Y=u²/(rho+sqrt(rho²-u²))`.
- `u1 <= u <= u2`: `Y=2*rho*sin(phi/2)²+(u-u1)*tan(phi)`.
- `u > u2`: `Y=H-(1/2-u)²/(rho+sqrt(rho²-(1/2-u)²))`.

`H=(1-q)*tan(phi)/2+q*tan(phi/2)/2`, `y=l2*Y`. Rationalisierte Kreisformeln vermeiden Auslöschung nahe der flachen Lösung.

## 3. Formfit ohne Längenbedingung

Minimiert wird `sum((y_fit(x_i)-y_cos(x_i))²)` an denselben 1001 x-Stützstellen. Symmetrie erlaubt 501 Auswertungen: doppelte Gewichte außer am Scheitel. Keine Normalabstände, kein CAD-Spline, keine Längenoptimierung. Definitionsbereich: positive Radien und Geraden, `0<q<1`, `0<phi<pi/2`. Zwei deterministische Nelder-Mead-Läufe starten mit `q=0.3,0.7`, `z=1`, wobei `phi=z*atan(2*pi*a)`; initiale Simplexschritte 0,05 und 0,1. Abbruch bei Simplex-Ausdehnung <1e-9, maximal 400 Iterationen je Start. Nichtkonvergenz oder degenerierte Grenzen führen zu einem Fehler. Dies ist kein allgemeiner Beweis eines globalen Minimums. Eine unabhängige verschachtelte Golden-Section-Suche bestätigt den Referenzfall.

Die Formfit-Polygonlänge verwendet wieder exakt 1000 x-Abschnitte. Der analytische Längenwert wird getrennt ausgewiesen. Beide werden gegen `l1` verglichen; positiver Fehler bedeutet zu lang. Das Höhenmaximum und die vertikalen Residuen stammen aus dem Fit. RMS = `sqrt(SSE/1001)`; Maximum nur auf den Stützstellen, kein Beweis eines kontinuierlichen Maximums.

## 4. Flacher Grenzfall und Bereich

Bei genau `l1=l2`: `A=h=phi=0`, beide Geraden je `l2/2`, Fitlänge `l2`, Fehler null. Kreis-/Kosinusradien sind undefiniert (Python `None`, VBA `Empty`), keine künstliche Nullradius-Dehnung. Falls eine Dicke angegeben ist, ist die vereinfachte Dehnungsabschätzung null; sonst fehlt sie.

Validiert: `0.001 <= l1,l2 <= 1e6`, `l2 <= l1 <= 2*l2`, optionale Dicke `0..1e6`. Boolesche Werte, nicht numerische Typen, NaN und Unendlich sind unzulässig. Die Python-Diagnoseoption `segments` erlaubt gerade ganze Zahlen 100..20000; **Standard und CAD-UIs bleiben 1000**. Höhere Segmentzahlen verändern die Excel-Semantik und dienen nur der Konvergenzdiagnose. VBA hat absichtlich keine veränderbare Segmentoption.

## 5. Radius und sehr vereinfachte Dehnung

Excel-Blatt `check cracks`: `r_excel=l2²/(2*pi²*A)`; unverändert als **Excel-Abschätzung** ausgegeben. Aus `y''(0)=4*pi²*A/l2²` folgt `r_correct=l2²/(4*pi²*A)`, separat als **korrigierter Kosinusradius**. Das Radiusverhältnis ist exakt zwei.

Optionale Dehnung in Prozent = `100*t/(2*r)`. Keine Fließkurve, neutrale Faser, Werkzeugreibung, Dickenänderung, plastische Vorgeschichte oder mehrachsige Spannungen. Daraus folgt keine Aussage über Risse, Herstellbarkeit oder Freigabe.

## 6. Felder und gemeinsame Referenzen

`reference/cases.csv`: original vorgegebener Zahlenfall 40/30/2, flach 30/30/2, homogene Skalierung 80/60/4. Keine Extraktion einer Arbeitsmappe. Toleranzen: dimensionale Fitwerte 1e-6 mm * (l2/30), Winkel 1e-5 Grad. Solverhistorie und gerundete Referenzwerte erlauben keine Bitgleichheit. Der beobachtete Unterschied im Referenzfall ist deutlich kleiner.

VBA-Rückgabe von `WrinkleCalculate(l1,l2,thickness)` ist ein nullbasiertes Variant-Array:

| Index | Python-Feld | Einheit |
|---:|---|---|
| 0 | amplitude_mm | mm |
| 1 | radius_mm | mm / Empty |
| 2 | height_mm | mm |
| 3 | phi_deg | Grad |
| 4 | straight_mm | mm je Seite |
| 5 | fit_polygon_mm | mm |
| 6 | fit_analytic_mm | mm |
| 7 | length_error_pct | % gegen l1 |
| 8 | rms_form_error_mm | mm |
| 9 | max_form_error_mm | mm, nur Stützstellen |
| 10 | cosine_radius_excel_mm | mm / Empty |
| 11 | cosine_radius_corrected_mm | mm / Empty |
| 12 | arc_strain_pct | % / Empty |
| 13 | cosine_strain_excel_pct | % / Empty |
| 14 | cosine_strain_corrected_pct | % / Empty |
| 15 | vertical_sse_mm2 | mm² |
| 16 | segments | 1000 |

Python liefert zusätzlich `analytic_length_error_pct`, Eingabelängen und Iterationszahl des ausgewählten Laufs. `thickness=None`/VBA `Empty` bedeutet keine Dickenabschätzung; Dicke null bedeutet explizit null.
