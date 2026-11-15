# CATIA V5 R32: Arbeitsplatztest

**Status: VBA-Quellen und UserForm-Code; VBA-Kompilierung, CATIA-Laufzeit, native UI-Importe, Lizenzen und reale Installation sind auf diesem Mac ungetestet.** Eine `.catvba` ist ein vom Zielhost erstelltes Projekt, keine umbenannte Textdatei. Eine zuverlässige CATVBA-/FRX-Erzeugung ist hier nicht möglich; deshalb werden keine solchen Binärdateien vorgetäuscht.

## Voraussetzungen und Quellen

Windows-Arbeitsplatz mit CATIA V5 R32 und installiertem/erlaubtem VBA-Editor samt Microsoft Forms. Die genaue Verfügbarkeit von VBA und Makroausführung mit IT/Lizenzadministration prüfen. Keine Excel-Installation, kein Solver und kein Excel-Objektmodell nötig. Makros nach der Unternehmensrichtlinie freigeben; keine globalen Sicherheitsrichtlinien abschalten.

`cad/catia/WrinkleCore.bas` ist der reine Rechenkern. Er nutzt nur VBA-Arithmetik, Variant-Arrays und Standardfunktionen; keine CATIA-/Excel-Objekte. `Launch.bas` öffnet das Formular. `UserForm-code.txt` ist **nur einzufügender Code**, kein importierbares `.frm` oder `.frx`.

Die Windows-CI führt denselben Kern nach Entfernung der Exportzeile `Attribute VB_Name` im VBScript-Host aus. Das prüft Zahlen und gemeinsame Sprachsemantik, **keine VBA-Kompilierung, keinen Forms-Designer und keinen CATIA-Import**. Windows Script Host ist eine Testabhängigkeit, keine Laufzeitabhängigkeit des späteren CATVBA-Prototyps. Falls WSH durch Unternehmensrichtlinie fehlt, nicht aktivieren; den Kern im erlaubten VBA-Host prüfen.

## 1. Echtes CATVBA-Projekt im Host erstellen

1. CATIA starten, optional ein leeres Testteil öffnen. Keine produktiven Dokumente nötig.
2. Über **Tools > Macro > Macros** den Makrodialog öffnen und **Macro libraries** wählen. Den Bibliothekstyp **VBA Projects** wählen und ein neues Projekt `WrinkleSourcePreview.catvba` im lokalen Testordner erstellen/registrieren. Englische UI-Begriffe dienen als Suchbegriffe; Rolle/Sprache kann abweichen.
3. Den **Visual Basic Editor** über Tools > Macro öffnen. Im neu erstellten Projekt **File > Import File** aufrufen und `WrinkleCore.bas` sowie `Launch.bas` importieren. Im Projekt müssen die Module exakt `WrinkleCore` und `Launch` erscheinen. Es dürfen keine doppelten/nummerierten Module entstehen.
4. Unter **Insert > UserForm** ein Formular erstellen und dessen `(Name)` auf **`frmWrinkle`** setzen. Erst das von CATIA gespeicherte Projekt ist eine echte `.catvba`.

Microsoft beschreibt den [Import von BAS-/FRM-/CLS-Komponenten](https://learn.microsoft.com/en-us/office/vba/language/reference/user-interface-help/import-file-dialog-box) und das [File-Menü des VBA-Editors](https://learn.microsoft.com/en-us/office/vba/language/reference/user-interface-help/file-menu). Ob diese Funktionen in genau dieser CATIA-Installation verfügbar sind, ist vor Ort zu prüfen. CATIA-spezifische Referenz ist die installierte R32 Automation/VBA-Hilfe beziehungsweise [Dassault Help](https://help.3ds.com/) (Zugang erforderlich).

## 2. UserForm exakt aufbauen

Formulargröße etwa Width 720, Height 540 Punkte; Caption `Faltenrechner - Source Preview - CAD ungetestet`. Toolbox-Klassen sind die normalen Microsoft-Forms-Controls. Labels für Eingabefelder mit mm ergänzen.

| Name | Typ | Eigenschaften / Position (Left, Top, Width, Height) |
|---|---|---|
| txtL1 | TextBox | (180, 15, 100, 22), Label `Abgewickelte Laenge l1 [mm]` |
| txtL2 | TextBox | (180, 45, 100, 22), Label `Projizierte Breite l2 [mm]` |
| chkThickness | CheckBox | (15, 80, 260, 22), Caption `Dickenabschaetzung aktivieren` |
| txtThickness | TextBox | (180, 110, 100, 22), Label `Wanddicke [mm]` |
| cmdCalculate | CommandButton | (320, 15, 160, 28), Caption `Berechnen` |
| cmdClose | CommandButton | (500, 15, 120, 28), Caption `Schliessen`, Cancel=True |
| txtResult | TextBox | (15, 155, 675, 340), MultiLine=True, ScrollBars=3 (Both), WordWrap=False, Locked=True, TabStop=False |

Den kompletten Inhalt von `UserForm-code.txt` in das Codefenster von `frmWrinkle` kopieren. Eventuell automatisch erzeugte leere Event-Prozeduren vorher entfernen, damit kein Name doppelt vorkommt. Eingaben werden mit `CDbl` nach Windows-Regionseinstellung gelesen: bei deutscher Einstellung Komma als Dezimaltrenner. Keine Tausendertrennzeichen eingeben. Die Startwerte sind ganzzahlig und unabhängig davon.

## 3. Kompilieren und starten

Im VBA-Editor **Debug > Compile** für das Projekt ausführen; Fehler protokollieren, keine Referenzprüfung deaktivieren. Unter **Tools > References** darf keine `MISSING`-Referenz stehen. Für diesen Prototyp keine Excel-Bibliothek hinzufügen. Projekt speichern, Editor schließen. Im Makrodialog das `Launch.CATMain` aus dem Projekt ausführen. Erwartet wird die native UserForm. Erst ein erfolgreicher Compile, Speichern, Schließen und erneutes Öffnen bestätigt die lokale Verpackbarkeit; hier wurde das nicht durchgeführt.

## 4. Numerik und UI abnehmen

1. CATIA-Build/SP/HF, Windows-Version, VBA-/Forms-Verfügbarkeit, Makrofreigaben und Lizenzprüfung protokollieren.
2. 40/30, Dicke aktiv 2: A 6,139413268; R ≈5,0322554; Höhe ≈12,2342750; φ ≈49,8407463°; Gerade je Seite ≈11,3319680 mm. Polygon ≈40,1738373; analytisch ≈40,1738725; Fehler **+0,434593 %**. Keine automatische Längenkorrektur.
3. Form-RMS ≈0,096220; max. vertikale Abweichung ≈0,181006 mm. Dickenwerte ≈19,871805 % Kreis, ≈13,465240 % Excel-Kosinus und ≈26,930480 % korrigierter Kosinus; alle Beschriftungen kontrollieren.
4. 30/30 liefert flach, undefinierte Radien, null Fehler. 80/60/4 verdoppelt Längen. Dicke ausgeschaltet liefert keine Dehnungszahl. Referenzen und Toleranzen siehe `reference/cases.csv` und Mathematikdokument.
5. Leere Felder, Text, 29/30, negative Dicke bei aktivierter Option und l1>2*l2 müssen zum Fehler führen; Ergebnisfeld darf dann keinen früheren Erfolg als aktuelle Rechnung zeigen.
6. Berechnen mehrfach, Schließen, Escape und erneutes Öffnen prüfen. Geometrie-/Dokumentstatus vor und nach vergleichen; es soll kein Objekt erzeugt oder geändert werden.
7. Projekt speichern, CATIA schließen, frisch starten und Projekt erneut laden/ausführen. Erst diesen Schritt als erfolgreichen Import/Installation im Testprotokoll markieren.

Für einen unabhängigen Windows-Quelltest ohne CATIA aus dem Repository-Stamm: `python tools/run_vbscript_tests.py`. Nicht per Doppelklick auf `.bas` starten. Ein erfolgreiches WSH-Ergebnis ist weiter keine CAD-Freigabe.
