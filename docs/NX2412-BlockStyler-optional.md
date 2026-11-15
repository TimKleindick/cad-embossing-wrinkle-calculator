# NX 2412: Arbeitsplatztest

**Status: ausführbare Python-Quellen; NX-Laufzeit, Block-Styler-Import, API-Kompatibilität, Lizenz und Installation sind auf diesem Mac ungetestet.** Es liegt absichtlich keine erfundene `wrinkle.dlx` bei. Eine Datei mit dieser Endung wäre ohne Prüfung im passenden NX-Designer kein belastbares Lieferpaket.

## Voraussetzungen

NX 2412 auf dem Arbeitsplatz, dessen NX Open Python und der Zugriff auf Block Styler. Die installierte Python-Version in der NX-Hilfe beziehungsweise mit einem kurzen Journal `import sys; print(sys.version)` prüfen. Der Kern benötigt nur `math`; der Adapter zusätzlich `pathlib` und `NXOpen`. Keine externe Python-Umgebung in den NX-Prozess injizieren.

Die tatsächlich nötigen NX-Open-/Block-Styler-Autorisierungen hängen von Installation und Lizenzkonfiguration ab. Vor Ort prüfen, ob der Designer geöffnet und das generierte Beispiel abgespielt werden kann; hier wurde weder ein Lizenzserver erreicht noch eine konkrete Lizenz-SKU bestätigt. Keine Lizenz oder Herstellerbibliothek wird mitgeliefert.

## 1. Quellen vorbereiten

Repository in einen lokalen Testordner kopieren oder den geprüften Source-Preview entpacken. Ordnerstruktur erhalten: `cad/nx/wrinkle_dialog.py` und `wrinkle/core.py` müssen zwei Ebenen auseinander liegen. Für diesen Test ein leeres Testteil in **mm** öffnen; die Zahlen sind unabhängig von Teil-Einheiten immer mm. Bestehende Kundenteile werden nicht benötigt.

Optional außerhalb NX die Referenzrechnung mit `python -m wrinkle 40 30 --thickness 2` prüfen. Das bestätigt keine NX-Funktion.

## 2. Native Maske im Block Styler erstellen

In NX den Befehl **Block Styler** über den Befehlsfinder öffnen (Menüpfade hängen von Rolle/Sprache ab). Neues Dialoglayout erstellen, Dialogtyp mit **OK / Apply / Cancel** wählen. Titel `Faltenrechner - Source Preview - CAD ungetestet`. Eine Gruppe `inputs` anlegen. Folgende Blöcke hinzufügen; **Block-ID exakt übernehmen**, keine Expressions mit Teil-Einheiten verwenden:

| Block-ID | Typ | Beschriftung | Startwert |
|---|---|---|---:|
| l1_mm | Double | Abgewickelte Laenge l1 [mm] | 40 |
| l2_mm | Double | Projizierte Breite l2 [mm] | 30 |
| use_thickness | Toggle / Check Box (boolesches Value) | Dickenabschaetzung aktivieren | false |
| thickness_mm | Double | Optionale Wanddicke [mm] | 2 |

Für Längenblöcke Min 0,001 und Max 1.000.000 einstellen, Dicke Min 0 und Max 1.000.000. Die Kernprüfung bleibt maßgeblich. Als Hinweislabel ergänzen: `Excel-Standard: 1000 Segmente; Formfit ohne Laengenbedingung; keine Materialfreigabe.`

Layout **als `cad/nx/wrinkle.dlx` im Testordner** speichern. Python-Beispielcode durch den Designer separat generieren lassen und prüfen, dass er `UI.CreateDialog`, `TopBlock.FindBlock`, `Double.Value`, boolesches `.Value` und die Handler `AddInitializeHandler`, `AddApplyHandler`, `AddOkHandler` in der installierten NX-Version verwendet. Falls der Toggle in diesem Designer anders heißt, den vom Designer erzeugten Block mit booleschem `Value` verwenden. Bei abweichenden Signaturen anhalten und Abweichung protokollieren; dieser Schritt ist die noch ausstehende API-/Importprüfung.

Der mitgelieferte Adapter verwendet ausschließlich diese Schnittstellen, `ListingWindow` und `NXMessageBox`. Er sucht die DLX über den absoluten Pfad neben sich. Keine Suchpfad- oder globale NX-Konfiguration erforderlich.

## 3. Journal abspielen

Über **Journal > Play** im Befehlsfinder `cad/nx/wrinkle_dialog.py` auswählen. Erwartet wird die native Maske; fehlt die DLX, muss eine verständliche Fehlermeldung erscheinen. **Apply** berechnet und schreibt die Ergebnisse in Listing Window und NX-Dialog; **OK** berechnet und schließt nach erfolgreichem Callback. Cancel schließt. Diese UI-Vorgänge sind hier noch nicht beobachtet worden.

## 4. Abnahme am Arbeitsplatz

1. NX-Build, Betriebssystem, eingebettete Python-Version und verfügbare Lizenzfunktionen notieren.
2. 40 / 30 / 2 mit aktivierter Dickenabschätzung: A ≈6,139413268; R ≈5,0322554; Höhe ≈12,2342750; φ ≈49,8407463°; Gerade je Seite ≈11,3319680 mm. Polygon ≈40,1738373 und analytisch ≈40,1738725 mm.
3. Anzeige der Längenabweichung **+0,434593 %** und des nicht erreichten 0,1-%-Ziels kontrollieren. Form-RMS ≈0,096220, Maximum ≈0,181006 mm. Excel-/korrigierte Kosinusabschätzungen müssen getrennt sein.
4. 30 / 30: Höhe und Fehler null, Radien `entfaellt`. Dicke ausgeschaltet: keine Dehnungszahlen. 80 / 60 / 4: dimensionale Ergebnisse verdoppelt, relative Fehler und Dehnung gleich.
5. 29 / 30, negative Dicke bei aktivierter Option und l1 >2*l2: Eingabe zurückweisen; kein alter Ergebniswert als neue Berechnung ausgeben.
6. Apply mehrfach, OK, Cancel und erneutes Öffnen testen. Prüfen, dass Teilnavigator, Geometrieanzahl und Änderungsstatus unverändert bleiben. Der Quellcode enthält keine Geometrieaufrufe; dies ersetzt diese CAD-Prüfung nicht.
7. Eingaben und Ergebnisse in einem neuen Testprotokoll festhalten; Original-Excel nicht anhängen oder in Git kopieren. Erst danach native DLX-Verteilung separat prüfen.

Offizielle versionsgebundene Referenz ist die mit NX 2412 installierte **NX Open Python Reference / Block UI Styler** beziehungsweise der [Siemens Support Center](https://support.sw.siemens.com/). Die geschützte aktuelle API-Dokumentation war hier nicht zuverlässig zugänglich; ältere oder fremde Spiegel wurden nicht als Nachweis für NX 2412 verwendet.
