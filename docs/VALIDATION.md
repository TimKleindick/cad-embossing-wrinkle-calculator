# Verifikationsprotokoll

Stand: 2026-11-15, Mac mit Python 3.13.1. Das Repository war leer und wurde in einen getrennten Checkout auf `feat/excel-compatible-source-preview` geklont; keine vorhandenen Änderungen überschrieben. Keine AGENTS.md oder `.agents/skills` im Checkout vorhanden. GitHub-Identität TimKleindick und privater Repository-Status wurden bestätigt.

## Lokal tatsächlich ausgeführt

- TDD-Rechenkern: 9 Tests vor der Umsetzung gegen explizite `NotImplementedError`-Platzhalter ausgeführt: erwarteter roter Lauf (28 Subtest-Fehler wegen fehlender Berechnung). Danach grün. Referenzen, unveränderte 1000-Segment-Semantik, flacher Fall, ungültige Eingaben, homogene Skalierung, Radiuskonventionen, Konvergenz sowie Symmetrie, Endpunkte und Tangentialität.
- TDD-Paketbau: zunächst 4 Tests mit 11 fehlenden-Verhalten-Fehlern gegen Platzhalter; danach grün. Zusätzlich staged-Blob-Täuschung, manipuliertes Manifest und unerlaubte zusätzliche Archiveinträge geprüft. Workbook-Bytes in diesen Tests sind synthetische Kleinstsignaturen, keine Originaldatei.
- CLI-Test zuerst rot mit `No module named wrinkle.__main__`, anschließend grün mit JSON-Referenz und unzulässigem Eingabefall.
- Gesamtlauf: `python3 -m unittest discover -s tests -v` — zunächst 16, nach ZIP-Plattformregression 17 Tests, grün.
- Python-Syntaxprüfung: `python3 -m compileall -q wrinkle cad/nx tools` (kein NX-Import dabei).
- Unabhängiger mathematischer Gegencheck: `python3 -m tools.independent_check`, verschachtelte Golden-Section-Suche mit grober Winkelsuche statt des produktiven Nelder-Mead; zusätzlich Simpson-Integration der kontinuierlichen Kosinuslänge. Keine Wiederverwendung der produktiven Solverfunktionen zur Erwartungsberechnung.

Der unabhängige Referenzfit ergab A=6,139413268036, R=5,032255388979, φ=49,840746273028°, Höhe=12,234275003659, Gerade=11,331968037174 mm, Polygon=40,173837278632, analytisch=40,173872488835 mm. Unterschiede zu den übergebenen Excel-Zahlen <1,1e-7 in der jeweiligen Einheit. Produktiver Fit: Polygon ≈40,173837277456, analytisch ≈40,173872487659 mm. Globale Optimalität über alle Eingaben wird nicht behauptet.

| Diagnose-Segmente | A [mm], unabhängige Rechnung | Fit-Polygonlänge [mm] |
|---:|---:|---:|
| 500 | 6,139443564951 | 40,173812471217 |
| **1000, Standard** | **6,139413268036** | **40,173837278632** |
| 2000 | 6,139405693840 | 40,173842859126 |
| 4000 | 6,139403800293 | 40,173843953457 |

Das 0,1-%-Längenziel ist beim Excel-Standardfall nicht erreicht: +0,434593 %. Keine Standardsemantik zur Zielerfüllung verändert. Keine Arbeitsmappe wurde eingelesen oder gespeichert; es wurden ausschließlich die vorgegebenen Formeln und Zahlen repliziert.

## Windows-CI und noch offene Hostprüfungen

[GitHub-CI-Lauf 43723275112](https://github.com/TimKleindick/cad-embossing-wrinkle-calculator/actions/runs/43723275112) für Commit `72190950f290f3ec6bb4c09453f72ca5b804bcf1`: **alle drei Jobs erfolgreich** (Ubuntu Python 3.11, Ubuntu Python 3.13, Windows Python 3.13). Je Job 16 Python-Tests, staged-Blob-Audit, Syntaxprüfung und Positivlisten-Paketbau erfolgreich. Der Windows-Job führte zusätzlich den echten `.bas`-Kern erfolgreich mit Start-Locale 1033 (en-US) und 1031 (de-DE) aus: je drei gemeinsame Referenzen plus Skalierung, flach/nahe-flach, Bereichsende, Eingaben, Dehnung, Form und Tangentialität. Die absichtlich mutierte Excel-Radiusformel wurde vorher erwartungsgemäß mit `FAIL: Excel strain` erkannt (negative Kontrolle). Normale CI hat keine Artefakte hochgeladen.

[Folge-CI 43723532495](https://github.com/TimKleindick/cad-embossing-wrinkle-calculator/actions/runs/43723532495) für `557fa80bac06b196806999a2a4622ce0ecd0a5e1` bestätigte erneut alle drei Jobs und beide Windows-Locale-Läufe; hochgeladene Artefakte: **0**. Die ersten plattformabhängigen Paket-Hashes hatten zwei Ursachen: Checkout-Zeilenenden und ZIP-Creator-System. `.gitattributes` erzwingt LF; der Builder setzt jetzt zusätzlich einheitliche POSIX-Creator-Metadaten. Ein neuer Regressionstest variierte das reale ZipInfo-Plattformdefault: erst beobachtete Byte-Ungleichheit (rot), nach der expliziten Einstellung grün. Inhaltsschutzprüfungen bleiben unverändert. Die Prüfung der finalen Push-CI und ihrer Hashes erfolgt im Abschlussbericht. Der VBA-Test wurde vor dem Kern geschrieben; ein roter VBA-Lauf **vor Implementierung** konnte auf dem Mac nicht beobachtet werden. Es wird kein vollständiger nativer VBA-TDD-Nachweis behauptet. CI führt den tatsächlichen `.bas`-Kern ohne Export-Metadaten mit `cscript.exe` aus; das ist eine zusätzliche Sprach-/Numerikprüfung und keine VBA-Kompilierung.

**Offen/ungetestet:** NX 2412 Laufzeit und Python-Integration, Block-Styler-Designer und DLX-Import, CATIA V5 R32, VBA-Kompilierung/Forms/CATVBA-Speichern und erneutes Importieren, beide Lizenzkonfigurationen und reale Arbeitsplatzinstallation. Die native UI wurde nicht angezeigt. Kein CAD-Binärpaket geliefert. Der Release-Workflow wurde nicht publizierend ausgeführt. Windows Script Host kann auf Unternehmensgeräten deaktiviert oder nicht installiert sein; keine Richtlinien umgehen.

Abnahmefolgen und zu protokollierende Werte stehen in den beiden Arbeitsplatzanleitungen. Erst deren tatsächlicher Durchlauf darf den CAD-Status ändern.


## Erweiterung: vorbereitete Ein-Datei-Einstiege

Die reinen Rechenkerne `wrinkle/core.py` und `cad/catia/WrinkleCore.bas` bleiben unverändert. `tools/build_entries.py` bindet sie in `ready-to-run/NX_WrinkleCalculator.py` und `ready-to-run/CATIA_WrinkleCalculator.CATScript` ein. Neue vier Tests wurden zuerst rot beobachtet (fehlende Einstiegskomponenten), danach grün. Gesamtlauf jetzt **21 lokale Tests**; Python-Syntaxprüfung, unabhängiger mathematischer Gegencheck und Generierungsprüfung bestanden. Der NX-Einstieg wurde als einzige Datei in einen leeren Ordner kopiert und seine Rechnung mit isoliertem Python ausgeführt.

Der nächste Windows-CI-Lauf führt die erzeugte CATScript-Quelle nach Entfernung der damaligen `Language`-Zuweisung und Neuplatzierung von `Option Explicit` mit kontrollierter Ein-/Ausgabe aus: Dezimalpunkt/-komma, drei Ergebnis-Seiten, ungültige Eingaben, leere Eingaben und Abbrechen. Zusätzlich wird der tatsächliche generierte Windows-Dialog in einem separaten Python-Prozess aus einem leeren Verzeichnis erzeugt und bedient. Dieser Test verwendet kein NX. Dessen tatsächlicher Status wird nach dem Push im Abschluss geprüft.

Die Paket-Positivliste umfasst jetzt 32 ausdrücklich benannte Quellen einschließlich der beiden Startdateien und der optionalen älteren Designer-Anleitungen. Es werden keine DLL, EXE, DLX, FRX oder CATVBA geliefert. Die detaillierten Hauptanleitungen beschreiben Download/Entpacken, Startdatei, konkrete CAD-Menüs, erforderliche Hostfunktionen, Sollwerte, Abbruch und Fehlerdiagnose. Native Windows-Dialogausführung und kontrollierte VBScript-Ausführung ersetzen keine NX-/CATIA-Integration. Lizenz-/Engine-Verfügbarkeit und konkrete Hostmenüs bleiben dort offengelegt ungetestet.


[Direktstart-CI 43726095118](https://github.com/TimKleindick/cad-embossing-wrinkle-calculator/actions/runs/43726095118), Commit `9627bab3a971a91d3b205ff05b73b64d208f3627`: **vier Jobs erfolgreich**, Ubuntu Python 3.10/3.11/3.13 sowie Windows Python 3.13. Windows hat den tatsächlichen Win32-Dialog aus einer einzeln kopierten Datei geöffnet, 40/30/2 berechnet, Dezimalkomma, ungültige Eingabe ohne veraltete Erfolgsausgabe, flachen Fall mit deaktivierter Dicke und Schließen geprüft. Der erzeugte CATScript-Quellcode bestand außerdem kontrollierte Ein-/Ausgabe-, Abbruch-, Fehler- und Ergebnis-Seitentests unter en-US/de-DE. Die bestehende negative Radiuskontrolle schlug erwartungsgemäß fehl, der echte Kern bestand.

Alle vier Jobs und der lokale Mac erzeugten ein identisches Paket mit SHA256 `86218be6175f5a0b04d8d40006bf633940ab212b0c609c2cd42a2c425dbfdc87`. Artefaktuploads: **0**. Das tatsächliche lokale ZIP wurde entpackt, die Generierungsprüfung und alle 21 Tests liefen daraus erfolgreich. Die folgende reine Dokumentationsaktualisierung ergänzt diese Nachweise und die vom Nutzer genannten Recherchehinweise; ihre finale CI wird im Abschluss erneut kontrolliert. **Kein NX-/CATIA-Hostlauf** wurde dadurch durchgeführt.

## CATScript-Startkorrektur

Ein Arbeitsplatztest in CATIA V5 R32 meldete `ScriptingERR_1002` bei `Option Explicit` in Zeile 2. Die ausgelieferte Datei begann mit einer `Language`-Zuweisung. Die frühere Windows-Prüfung entfernte beide Zeilen und konnte den Dateianfang deshalb nicht prüfen. Der Generator setzt jetzt `Option Explicit` an den Anfang und lässt die `Language`-Zuweisung weg. Ein Regressionstest ist am alten Dateianfang fehlgeschlagen und besteht mit der korrigierten Datei. Windows CI prüft zusätzlich die ausgelieferte Datei direkt mit `cscript`, bevor die Rechen- und Dialogablauftests laufen. Der erneute Start der korrigierten Datei in CATIA V5 R32 steht aus.
