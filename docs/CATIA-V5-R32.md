# CATIA V5 R32: vorbereitete Datei starten

## Lieferumfang und Status

Startdatei: **`ready-to-run/CATIA_WrinkleCalculator.CATScript`**. Sie enthält den unveränderten VBA/VBScript-kompatiblen Kern und den vollständigen Makroeinstieg. Native **InputBox-/MsgBox-Dialoge** fragen die Werte ab und zeigen drei Ergebnis-Seiten. Kein CATVBA-Projekt, keine UserForm-Erstellung, kein Import von BAS-/FRM-Dateien, keine Excel-Installation und kein externer Python-Aufruf erforderlich.

Die bequemere zusammenhängende UserForm bleibt als [optionale Ausbauanleitung](CATIA-V5-R32-UserForm-optional.md). Für dynamische CATVBA-UserForms aus einem reinen Skript ohne Formular-/Projektabhängigkeit wurde kein belastbar dokumentierter CATIA-Weg gefunden. Daher ist die vorbereitete Folge nativer Dialoge die konkrete Standardalternative. Es wird keine allgemeine technische Unmöglichkeit behauptet.

**CATIA V5 R32, Makroregistrierung, tatsächliche Eingabe-/Ausgabedialoge im Host, Skript-Engine, Lizenzen und reale Arbeitsplatzinstallation bleiben ungetestet.** Windows-CI führt den tatsächlichen Makro-Quellcode mit kontrollierter Ein-/Ausgabe aus; sie startet CATIA nicht.

## 1. Dateien beziehen und entpacken

1. Das [Repository auf dem Hauptbranch main](https://github.com/TimKleindick/cad-embossing-wrinkle-calculator/tree/main) öffnen. Bei noch privater Sichtbarkeit mit dem berechtigten GitHub-Konto anmelden.
2. **Code > Download ZIP** anklicken und lokal speichern, zum Beispiel unter `C:\CAD-Test\Wrinkle`.
3. Im Windows-Explorer **Alle extrahieren…** verwenden. Den entpackten Hauptordner und darin **`ready-to-run`** öffnen. Nicht den ZIP-Inhalt direkt registrieren.
4. Die Datei muss exakt **`CATIA_WrinkleCalculator.CATScript`** heißen. Dateiendungen einblenden; `.CATScript.txt` ist falsch. Die aktuelle Datei beginnt mit `Option Explicit`. Alternativ nur diese eine Datei über GitHubs **Download raw file** beziehen; sie benötigt keine Begleitdateien.
5. Den Quell-Commit aus der GitHub-Dateiansicht für das spätere Protokoll notieren. Ein gebautes Source-Preview-ZIP darf ebenfalls vollständig entpackt werden; der gleiche Unterordner enthält die Startdatei. Für diesen Auftrag wurde kein Release veröffentlicht.

Keine Original-Excel in das Repository oder Testprotokoll kopieren. Die Makrodatei lädt keine Arbeitsmappe und schreibt keine Ergebnisdatei.

## 2. Voraussetzungen und Einstellungen

- Windows-Arbeitsplatz mit **CATIA V5 R32** und erlaubter Skript-Makroausführung. Eine konkrete zusätzliche Lizenz-SKU ist anhand der verfügbaren Quellen nicht bestätigt; Lizenz-/Makrofreigaben vor Ort mit IT prüfen.
- Funktionierende **VBScript-Skript-Engine** in der unterstützten CATIA-/Windows-Konfiguration. Das Makro ruft weder `wscript.exe` noch `cscript.exe` auf; diese werden nur für externe CI-Tests benutzt.
- Kein VBA-Editor und keine Microsoft-Forms-Installation für diesen Startweg vorgesehen. Keine Makro-Sicherheitsrichtlinie global abschalten und keine externen COM-Form-Klassen registrieren.
- Microsoft kündigt VBScript ab und führt es als Windows Feature on Demand. Fehlt die Engine, ist dies eine zu klärende Installations-/IT-Frage, kein Anlass, Unternehmensrichtlinien zu umgehen. Die konkrete R32-/Windows-Kombination wurde hier nicht getestet.

## 3. Genau im CAD registrieren und starten

1. CATIA V5 R32 normal starten. Der Rechner verwendet keine Dokumentobjekte; produktive CATParts/CATProducts sind nicht nötig. Falls die lokale Oberfläche ein Dokument zum Aktivieren der Menübefehle verlangt, ein neues leeres Testteil verwenden.
2. **Tools > Macro > Macros…** öffnen (je nach Oberfläche **Extras > Makro > Makros…**).
3. Im Makrodialog **Macro libraries…** anklicken.
4. Bei **Library type / Bibliothekstyp** **Directories / Verzeichnisse** wählen. **Nicht VBA Projects** wählen.
5. **Add existing library… / Vorhandene Bibliothek hinzufügen…** wählen und genau den entpackten Ordner **`ready-to-run`** auswählen, in dem die `.CATScript` liegt. Mit **OK** bestätigen.
6. Mit **Close / Schliessen** zur Makroliste zurückkehren. Falls nötig die soeben registrierte Verzeichnisbibliothek auswählen.
7. Das Makro **`CATIA_WrinkleCalculator`** beziehungsweise den vollständigen `.CATScript`-Dateinamen auswählen und **Run / Ausführen** drücken. CATIA soll dessen `CATMain` selbst aufrufen; die Datei nicht umbenennen und keinen zusätzlichen Aufruf hineinkopieren.
8. Erwartet wird die erste Eingabebox für l1. Die Bezeichnung der Menüs und die Registrierung sind durch ältere V5-Hersteller-Supportfälle belegt; die exakte Darstellung in R32 ist ausdrücklich noch am Arbeitsplatz zu bestätigen.

Die Bibliotheksregistrierung ist normalerweise der einmalige Vorbereitungsschritt. Beim nächsten Test Makrodialog öffnen, dieselbe Bibliothek/Makrodatei auswählen und Run drücken. Ob die lokale R32-Konfiguration die Bibliothek über einen Neustart speichert, muss einmal überprüft werden.

## 4. Eingabefolge und Sollvergleich

1. **Abgewickelte Laenge l1**: `40`, mit OK bestätigen.
2. **Projizierte Breite l2**: `30`, mit OK bestätigen.
3. **Optionale Dickenabschaetzung berechnen?**: **Ja** wählen.
4. **Optionale Wanddicke**: `2`, mit OK bestätigen.
5. Es folgen drei mit **1/3, 2/3, 3/3** betitelte Ergebnisdialoge. Werte ablesen und jeweils mit OK weitergehen. **Strg+C** kopiert bei einer normalen Windows-Meldungsbox üblicherweise deren Text; dies am Arbeitsplatz prüfen oder Werte ins Testprotokoll übertragen.

Alle Eingaben sind mm. Ein Punkt oder ein Komma wird eindeutig als **Dezimalzeichen** interpretiert, z.B. `40,0` und `40.0` sind gleich. Keine Tausendertrennzeichen, Einheiten oder Exponenten verwenden; mehrdeutige gemischte Schreibweisen werden abgelehnt. Die Ausgabe folgt der Windows-Regionseinstellung.

| Seite | Größe | Soll, ungefähr |
|---|---|---:|
| 1 | A | 6,139413268 mm |
| 1 | R | 5,0322554 mm |
| 1 | Höhe | 12,2342750 mm |
| 1 | Winkel | 49,8407463° |
| 1 | Gerade je Seite | 11,3319680 mm |
| 2 | Excel-Polygonlänge | 40,1738373 mm |
| 2 | Analytische Fitlänge | 40,1738725 mm |
| 2 | Polygon-Längenabweichung | **+0,434593 %** |
| 2 | Vertikale Formabweichung RMS / maximal | 0,096220 / 0,181006 mm |
| 3 | Excel-/korrigierter Kosinusradius | 7,426529319 / 3,713264660 mm |
| 3 | Excel-/korrigierte Kosinus-Dehnung | 13,465240 / 26,930480 % |
| 3 | Kreisbogen-Dehnung | 19,871805 % |

Der Hinweis **`Laengenziel <0.1% NICHT erreicht`** gehört zum korrekten Excel-Standard. Es wird weiter mit 1000 Segmenten und Formfit ohne Längenbedingung gerechnet. Dehnung ist allein die stark vereinfachte `t/(2r)`-Abschätzung, keine Freigabe oder Risssicherheitsaussage.

## 5. Abbruch, Fehler und weitere Testfälle

- **Leer lassen oder Abbrechen** in einer Wertebox beendet den gesamten Lauf ohne Ergebnis. Eine leere Eingabe wird nicht zur Null umgewandelt. Das native InputBox-Verhalten unterscheidet leere Bestätigung und Abbrechen nicht sicher; beide sind deshalb ausdrücklich Abbruch.
- Bei der Dickenfrage bedeutet **Nein**: rechnen ohne Dickenabschätzung. **Abbrechen** beendet alles. Bei Ja muss eine nichtleere Dicke eingegeben werden; auch hier beendet Abbrechen den Lauf.
- Ungültige Eingaben liefern eine Fehlermeldung ohne Erfolgsseiten. Danach Makro erneut starten. Beispiele: `29/30`, `text`, negative Dicke. Unterstützt sind positive Längen 0,001..1.000.000 mm, `l2<=l1<=2*l2` und optionale Dicke 0..1.000.000 mm.
- `30/30`, Dickenfrage Nein: flach, A/Höhe/Winkel/Fehler null, Gerade je Seite 15, Fitlänge 30 mm, Radien undefiniert, Dehnungen nicht angegeben.
- `80/60/4`: Längen doppelt, Winkel, relative Fehler und Dehnungsabschätzungen unverändert.
- Nach allen drei Seiten muss CATIA normal bedienbar sein. Makro erneut starten und nach l1 abbrechen; danach einmal CATIA schließen/öffnen und die Registrierung erneut prüfen. Geometrieanzahl und Dokument-Änderungsstatus sollen unverändert bleiben.

## 6. Fehlerdiagnose und Protokoll

| Beobachtung | Konkrete Prüfung / nächster Schritt |
|---|---|
| Makro erscheint nicht | Ordner statt ZIP gewählt? Bibliothekstyp Directories? Liegt die `.CATScript` direkt in diesem Ordner? Endung nicht `.txt`? |
| Projekt-/Formularimport wird verlangt | Falscher Startweg: für diese Datei kein CATVBA-Projekt und keinen VBA-Editor verwenden. Zur Verzeichnis-Makrobibliothek wechseln. |
| `ScriptingERR_1002` bei `Option Explicit` in Zeile 2 | Aktuelle Raw-Datei herunterladen und die alte Kopie im registrierten Makroordner ersetzen. `Option Explicit` steht in der korrigierten Datei in Zeile 1. |
| Skript-Engine nicht verfügbar / Makro durch Richtlinie blockiert | Vollständige Meldung sowie CATIA-Build/SP/HF und Windows-Version erfassen. Unterstützte Engine/IT-Freigabe prüfen lassen; keine Sicherheitseinstellungen global senken. |
| Eingabebox verdeckt | Taskleiste/Alt+Tab und CATIA-Fokus prüfen. Frühe V5-Versionen hatten dokumentierte InputBox-Fokusprobleme; daraus wird kein Fehler in R32 abgeleitet. Modalität/Fokus sind Teil des offenen Tests. |
| Nach Abbrechen kein Ergebnis | Vorgesehen: abbrechen/leer beendet vollständig. Erneut Run wählen. |
| Zahl wird zurückgewiesen | Genau ein Dezimalzeichen, keine Gruppen-/Einheiten-/Exponentschreibweise; Wertebereich und l1/l2-Verhältnis prüfen. |
| Dehnungswerte fehlen | Dickenfrage bewusst Ja wählen und Dicke eingeben. Nein bedeutet keine Schätzung, nicht Dicke null. |

Protokollieren: Quell-Commit, CATIA-Build/SP/HF, Windows-Version, freigegebene Makro-/Engine-Konfiguration, tatsächlich geklickte Menüfolge, Eingaben/Ergebnisse, Abbruch und Neustarttest sowie unveränderte Dokument-/Geometriezustände. Keine Original-Excel anhängen. Erst bestandene Schritte als CAD-getestet markieren.

## Quellen und Grenzen der Belege

Die [CAA-V5-Makroregeln von Dassault Systèmes](https://catia-v5-help.anarkia333data.center/online/CAAScrTechArticles/CAAScrScriptCodingRules.htm) setzen `Option Explicit` an den Anfang und entfernen die `Language`-Zuweisung aus aufgezeichneten Makros. [IBM HE03301](https://www.ibm.com/support/pages/apar/HE03301) beschreibt den Verzeichnisbibliothek-Start für einen älteren V5-Stand. [Microsoft InputBox](https://learn.microsoft.com/en-us/openspecs/microsoft_general_purpose_programming_languages/ms-vbal/64b763ff-9f5f-43cd-b247-c75557e51989) erklärt das Abbruchverhalten, [Typkonvertierung](https://learn.microsoft.com/en-us/office/vba/language/concepts/getting-started/type-conversion-functions) die Locale-Abhängigkeit normaler Konvertierungen. Unser Parser vermeidet diese Mehrdeutigkeit. [Microsofts VBScript-Status](https://learn.microsoft.com/en-us/windows/whats-new/deprecated-features-resources) betrifft die Engine-Verfügbarkeit. Maßgeblich für R32 bleiben die installierte Automation-Hilfe und [Dassault Help](https://help.3ds.com/).


Zusätzlich geprüfter Recherchehinweis: Der [vom Nutzer genannte V5-Hilfespiegel „Running a Macro“](https://catia-v5-help.anarkia333data.center/online/basug_C2/basugbt1903.htm) beschreibt ebenfalls Tools > Macro > Macros und als weiteren Startweg den **Doppelklick auf `.CATScript`** mit passender Windows-Dateizuordnung. Das ist keine R32-Abnahme. Wenn die bestehende Dateizuordnung nachweislich auf Tims R32-Installation zeigt, kann Tim diesen optionalen Schnellstart testen; sonst den oben beschriebenen Verzeichnisbibliothek-Weg verwenden. Keine globale Dateizuordnung oder Kommandozeilenumgebung muss für unseren Standardweg verändert werden. Der Spiegel ist ein zusätzlicher Hinweis; die Hauptanleitung stützt die Makrokonvention auf die oben genannten Hersteller-Supportfälle.
