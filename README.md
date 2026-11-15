# Faltengeometrie-Rechner: Source Preview

Erste Rechenprototypen für **NX 2412** und **CATIA V5 R32**. Keine Geometrieerzeugung. **CAD-Laufzeit, VBA-Kompilierung, native UI-Importe, Lizenzen und reale Installation sind ungetestet.** Die Quellen ersetzen keine erprobten CAD-Installationspakete.

**Vorbereiteter Direktstart:** [`ready-to-run/NX_WrinkleCalculator.py`](ready-to-run/NX_WrinkleCalculator.py) in NX über **Journal > Play** öffnen; erzeugt seinen Windows-Dialog selbst. [`ready-to-run/CATIA_WrinkleCalculator.CATScript`](ready-to-run/CATIA_WrinkleCalculator.CATScript) in CATIA über eine **Directories-Makrobibliothek** starten; fragt Werte in nativen Eingabeboxen ab. Jede Datei enthält ihren vollständigen unveränderten Kern. Tim muss keine DLX, UserForm oder CATVBA erstellen.

Die Dateien vollständig herunterladen/entpacken und im jeweiligen CAD starten. Genaue Menüschritte, Einstellungen, Voraussetzungen, Sollwerte, Abbruch und Fehlerdiagnose stehen in den beiden Anleitungen unten. Der NX-Einstieg setzt Windows und `ctypes` im NX-Python voraus; der CATIA-Einstieg eine verfügbare VBScript-Engine und Makrofreigabe. Diese Hostvoraussetzungen sind ungetestet.

Die Standardrechnung repliziert die vorgegebene Excel-Mathematik: 1000-Segment-Polygonlänge für den Kosinus, danach vertikaler Formfit mit drei Kreisbögen und zwei Tangenten **ohne Längenbedingung**. Kein Excel/Solver, SciPy oder sonstiges Fremdpaket zur Laufzeit erforderlich.

```sh
python3 -m unittest discover -s tests -v
python3 -m wrinkle 40 30 --thickness 2
```

Python 3.10/3.11/3.13 wird in CI geprüft; NX verwendet seinen eigenen Python-Interpreter, dessen Kompatibilität am Arbeitsplatz zu prüfen ist. Kein `pip install` nötig. Unterstützter Prototypbereich: positive Längen von 0,001 bis 1.000.000 mm und `l2 <= l1 <= 2*l2`; optionale Wanddicke 0 bis 1.000.000 mm. Außerhalb wird abgebrochen. Das ist eine numerische Bereichsgrenze, keine Materialgrenze.

| Ergebnis für 40 / 30 mm | Excel-kompatibler Kern, gerundet |
|---|---:|
| Kosinus A | 6,139413268 mm |
| Kreisradius R | 5,0322554 mm |
| Winkel φ | 49,8407463° |
| Höhe | 12,2342750 mm |
| Gerade je Seite | 11,3319680 mm |
| Formfit-Polygonlänge | 40,1738373 mm |
| Formfit analytisch | 40,1738725 mm |
| Längenabweichung des Polygons | **+0,434593 %** |
| Vertikale Formabweichung RMS / maximal | 0,096220 / 0,181006 mm |

Das gewünschte Längenziel unter 0,1 % wird im Excel-Standardfall **nicht erreicht**. Der Standard wird deshalb nicht verändert. Formabweichungen beziehen sich auf die 1001 vertikalen Stützpunktabweichungen, nicht auf einen normalen Abstand oder einen Materialfluss.

Bei 2 mm Wanddicke: Excel-Kosinusabschätzung 13,46524 %, korrigierte Kosinusabschätzung 26,93048 %, Kreisbogenabschätzung 19,87181 %. Grundlage ist allein `t/(2r)`; **keine Materialfreigabe und keine Aussage zur Risssicherheit**. Die Excel-Radiusformel ist doppelt so groß wie der mathematisch korrekte Kosinusradius. Beide sind getrennt gekennzeichnet.

- [Mathematik und Ergebnisfelder](docs/MATHEMATICS.md)
- [NX 2412: vorbereitete Python-Datei starten](docs/NX2412.md)
- [CATIA V5 R32: vorbereitete CATScript-Datei starten](docs/CATIA-V5-R32.md)
- [Tatsächlich ausgeführte Prüfungen und Grenzen](docs/VALIDATION.md)
- [Quellpakete, Schutzprüfungen und Release-Verfahren](docs/RELEASES.md)

Die Original-Excel wird weder benötigt noch mitgeliefert. Niemals in dieses Repository kopieren. `.gitignore`, staged-Blob-Audit und Release-Positivliste schützen verschiedene Übergänge. Lokalen Commit-Hook aktivieren:

```sh
git config core.hooksPath .githooks
```

Referenzwerte in `reference/cases.csv` sind ausschließlich die vorgegebenen Zahlen und daraus skalierte Fälle; keine Arbeitsmappe oder internen Metadaten. Herstellerprodukte und ihre Lizenzen werden nicht mitverteilt.
