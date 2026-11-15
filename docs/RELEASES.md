# Quellpakete und sichere Releases

Die Original-Excel enthält interne Metadaten und darf **nie** in Git, CI-Artefakte oder Releases. Sie ist kein Build-Eingang. Auch keine umbenannten Kopien, Screenshots, eingebetteten Daten oder historischen Excel-Binärdateien einbringen. Die hier erstellten Zahlenreferenzen stammen aus der Aufgabenstellung.

## Schutzübergänge

- `.gitignore` blockiert typische Excel-Dateinamen, auch Großschreibung. Das ist kein Schutz gegen `git add -f`; deshalb zusätzlich vor jedem Commit den Hook aktivieren: `git config core.hooksPath .githooks`.
- `python tools/package_preview.py audit` prüft **staged Blob-Inhalte** aller regulären Git-Dateien: Dateinamen, UTF-8, Größe, ZIP/OLE-Magie und Workbook-XML. Das verhindert einen sauberen Working-Tree-Köder über einem unsicheren Index. Symlinks und Gitlinks werden abgelehnt. CI wiederholt den Audit.
- `PACKAGE_FILES` in `tools/package_preview.py` ist eine explizite, einzeln benannte Positivliste. Keine Ordnerarchive, keine Wildcards, keine externen Dateien. Einzig `reference/cases.csv` ist als CSV freigegeben. Neu aufgenommene Inhalte benötigen menschliche Prüfung; technische Filter können interne Metadaten in beliebigem Klartext nicht semantisch erkennen.
- Paketbau erfordert einen sauberen Commit. Fehlende Quellen, Symlinks, Workbook-Inhalte oder Fremdcontainer brechen vor der Ausgabe ab. Ein Manifest enthält Quell-Commit, CAD-Status und SHA-256 pro Datei. ZIP-Reihenfolge/Zeitstempel sind deterministisch. Die ZIP wird nach dem Bau erneut auf die genaue Positivliste und Prüfsummen geprüft.
- Normale CI lädt **keine Artefakte** hoch. Nur der manuelle Preview-Release-Workflow überträgt genau ZIP und SHA256-Datei mit einem Tag Aufbewahrung zwischen Jobs. Der Publisher prüft Manifest, Quell-Commit und ZIP-Hash und unmittelbar vor Veröffentlichung die Tag-Zuordnung erneut und hängt genau diese zwei Dateien an.

## Lokaler reproduzierbarer Build

Aus einem sauberen, getesteten Git-Checkout:

```sh
python3 -m unittest discover -s tests -v
python3 tools/package_preview.py audit
python3 tools/package_preview.py build
python3 tools/package_preview.py verify
```

Erzeugt `dist/wrinkle-source-preview.zip` und `.sha256`. `dist/` ist ignoriert. Vor erneutem Bau die vorherige Testausgabe außerhalb des Repositories ablegen oder gezielt entfernen; vorhandene Archive werden nicht überschrieben. Hashes belegen Integrität, keine Signatur oder CAD-Zertifizierung.

## Manueller Preview-Release

**Dieser Erstauftrag erstellt keinen Tag, kein Release und keinen Merge.** Der Workflow ist dafür vorbereitet, seine Publikation wurde nicht ausgeführt.

1. Branch nach Review auf `main` übernehmen und dort sämtliche CI-Prüfungen bestehen lassen. Kein Workflow läuft mit `pull_request_target` oder `workflow_run`; PR-Code erhält keine Schreibrechte.
2. Gewünschten geprüften `main`-Commit mit einem neuen Tag wie `v0.1.0-source-preview.1` markieren und den Tag pushen. Der Workflow erstellt oder verschiebt keine Tags.
3. Unter Actions den Workflow `Source preview release (CAD untested)` **auf main** manuell ausführen. Vorhandenen Tag eingeben und die bewusste Bestätigung `CAD UNTESTED SOURCE PREVIEW` exakt schreiben.
4. Der Prüfschritt akzeptiert nur das Preview-Tagmuster und einen existierenden Tag auf genau dem ausgewählten `main`-Commit. Python-Tests, staged-Quellaudit und der Windows-Kerntest müssen erneut bestehen. Erst der folgende Publisher-Job erhält `contents: write`; alle anderen Jobs nur `contents: read`. Actions sind auf volle offizielle Commit-SHAs gepinnt, Checkout speichert keine Zugangsdaten.
5. Ergebnis ist immer ein **Prerelease** mit `Source Preview - CAD UNTESTED` im Titel und dem unverifizierten CAD-Status in den Notizen. Bestehende Releases werden nicht überschrieben. Danach die beiden Assets herunterladen und Hash/Manifest sowie Status prüfen.

Die manuelle Bestätigung ist ein Workflow-Eingabegatter, **keine konfigurierte GitHub-Environment-Genehmigung**. Es wurden keine Branch-/Tag-Regeln oder Required Reviewers im Konto eingerichtet oder behauptet. Für spätere Teamverteilung zusätzlich geschütztes `main`, unveränderliche Release-Tags per Tagregeln, Reviewpflichten für `.github/` und Positivliste, sowie soweit im Kontoplan verfügbar ein Release-Environment mit erforderlichen Reviewern konfigurieren. [GitHubs Sicherheitsreferenz](https://docs.github.com/en/actions/reference/security/secure-use) erläutert minimale Rechte und SHA-Pinning. Das ersetzt nicht die Arbeitsplatzprüfung.

GitHub erzeugt zu Releases zusätzlich Quellarchive aus dem Tag. Daher muss die **gesamte getaggte Quellversion** sauber sein, nicht nur das angehängte ZIP. Die Workbook-Regel gilt auch für lokale Git-Historie: nie eine Originaldatei committen, selbst wenn sie danach wieder gelöscht würde.

Die erneute Tagprüfung reduziert eine Zuordnungsrace, kann jedoch keine atomare Tag-Unveränderlichkeit erzwingen. Für verbindliche Releases sind unveränderliche Release-Tags serverseitig erforderlich; hierfür wurde keine Konfiguration im Konto geändert.
