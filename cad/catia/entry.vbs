' Native CATScript adapter. No CATVBA project, UserForm, Excel or external COM form.
' The generator embeds the unchanged pure core above this source.
Class WrinkleDialogs
    Public Function Ask(ByVal prompt,ByVal initial)
        Ask=InputBox(prompt & vbCrLf & "mm; Punkt oder Komma, keine Tausendertrennzeichen. Leer/Abbrechen beendet.", _
                     "Faltenrechner - CAD ungetestet",initial)
    End Function
    Public Function ConfirmThickness()
        ConfirmThickness=MsgBox("Optionale Dickenabschaetzung berechnen?" & vbCrLf & _
            "Stark vereinfachtes t/(2r)-Modell; keine Materialfreigabe oder Risssicherheit.", _
            vbYesNoCancel+vbQuestion,"Faltenrechner - Source Preview")
    End Function
    Public Sub ShowResult(ByVal text,ByVal page)
        MsgBox text,vbOKOnly+vbInformation,"Faltenrechner - CAD ungetestet - " & page & "/3"
    End Sub
    Public Function ShowIllustrated(ByRef values, ByVal l1, ByVal l2, ByVal thickness)
        Dim succeeded
        On Error Resume Next
        Err.Clear
        succeeded = WOpenResult(values, l1, l2, thickness)
        ShowIllustrated = (Err.Number = 0 And succeeded = True)
        On Error GoTo 0
    End Function
    Public Sub ShowError(ByVal text)
        MsgBox "Fehler: " & text & vbCrLf & "Kein Ergebnis freigegeben. Makro erneut starten.", _
            vbOKOnly+vbExclamation,"Faltenrechner - Eingabe pruefen"
    End Sub
End Class

Function WParseDecimal(ByVal text)
    Dim i,ch,value,factor,sign,seenSeparator,digitsBefore,digitsAfter
    text=Trim(CStr(text))
    If Len(text)=0 Or Len(text)>32 Then Err.Raise 5,"WrinkleEntry","Zahl mit Punkt oder Komma erforderlich"
    sign=1
    If Left(text,1)="-" Then sign=-1
    If Left(text,1)="-" Or Left(text,1)="+" Then text=Mid(text,2)
    value=0.0: factor=1.0: seenSeparator=False: digitsBefore=0: digitsAfter=0
    For i=1 To Len(text)
        ch=Mid(text,i,1)
        If ch>="0" And ch<="9" Then
            If seenSeparator Then
                factor=factor*10
                value=value+(Asc(ch)-48)/factor
                digitsAfter=digitsAfter+1
            Else
                value=value*10+(Asc(ch)-48)
                digitsBefore=digitsBefore+1
            End If
        ElseIf (ch="." Or ch=",") And Not seenSeparator Then
            seenSeparator=True
        Else
            Err.Raise 5,"WrinkleEntry","Nur Zahl mit einem Punkt oder Komma; keine Gruppierung/Exponenten"
        End If
    Next
    If digitsBefore=0 Or (seenSeparator And digitsAfter=0) Then Err.Raise 5,"WrinkleEntry","Unvollstaendige Zahl"
    WParseDecimal=sign*value
End Function

Function WEntryNumber(ByVal value,ByVal unit)
    If IsEmpty(value) Then
        WEntryNumber="entfaellt / nicht angegeben"
    Else
        WEntryNumber=FormatNumber(value,9,-1,0,0) & " " & unit
    End If
End Function

Function WJsonNumber(ByVal value)
    If IsEmpty(value) Then
        WJsonNumber = "null"
    Else
        ' CStr does not group digits. Normalize the decimal mark for JSON.
        WJsonNumber = Replace(CStr(value), Mid(CStr(0.5), 2, 1), ".")
    End If
End Function

Function WResultData(ByRef values, ByVal l1, ByVal l2, ByVal thickness)
    Dim numbers(16), fit(200), i, phi, ordinate
    For i = 0 To UBound(numbers)
        numbers(i) = WJsonNumber(values(i))
    Next
    phi = values(3) * WPI / 180
    For i = 0 To UBound(fit)
        ordinate = 0
        If Not IsEmpty(values(1)) Then ordinate = WrinkleY(l2 * (i / 200), l2, values(1), phi)
        fit(i) = WJsonNumber(ordinate)
    Next
    WResultData = "{""l1"":" & WJsonNumber(l1) & ",""l2"":" & WJsonNumber(l2) & _
        ",""thickness"":" & WJsonNumber(thickness) & ",""values"":[" & Join(numbers, ",") & _
        "],""fit"":[" & Join(fit, ",") & "]}"
End Function

Function WOpenResult(ByRef values, ByVal l1, ByVal l2, ByVal thickness)
    Dim fs, shell, path, report, stream
    report = Replace(WResultTemplate(), "{{DATA}}", WResultData(values, l1, l2, thickness))
    Set fs = CreateObject("Scripting.FileSystemObject")
    Set shell = CreateObject("Shell.Application")
    path = fs.BuildPath(fs.GetSpecialFolder(2).Path, "Faltengeometrie-" & fs.GetTempName & ".html")
    Set stream = fs.CreateTextFile(path, False, False)
    stream.Write report
    stream.Close
    Call shell.ShellExecute(path, "", "", "open", 1)
    WOpenResult = True
End Function

Function WrinklePages(ByRef v,ByVal l1,ByVal l2)
    Dim a,b,c
    a="SOURCE PREVIEW - CATIA-Laufzeit/Import ungetestet" & vbCrLf
    a=a & "Excel: 1000 Segmente, Formfit ohne Laengenbedingung." & vbCrLf
    a=a & "l1 (Soll-Laenge entlang der Referenz): " & l1 & " mm" & vbCrLf
    a=a & "l2 (Breite zwischen den Endpunkten): " & l2 & " mm" & vbCrLf
    a=a & "A (Kosinus-Amplitude; Scheitel bei 2A): " & WEntryNumber(v(0),"mm") & vbCrLf
    a=a & "R (Radius der drei Kreisboegen): " & WEntryNumber(v(1),"mm") & vbCrLf
    a=a & "Hoehe: " & WEntryNumber(v(2),"mm") & vbCrLf & "Winkel: " & WEntryNumber(v(3),"deg") & vbCrLf
    a=a & "Gerade je Seite: " & WEntryNumber(v(4),"mm")
    b="Excel-Polygonlaenge: " & WEntryNumber(v(5),"mm") & vbCrLf
    b=b & "Analytische Fitlaenge: " & WEntryNumber(v(6),"mm") & vbCrLf
    b=b & "Polygon-Laengenabweichung: " & WEntryNumber(v(7),"%") & vbCrLf
    b=b & "Vertikale Formabweichung RMS: " & WEntryNumber(v(8),"mm") & vbCrLf
    b=b & "Max. vertikale Formabweichung: " & WEntryNumber(v(9),"mm") & vbCrLf
    If Abs(v(7))>=0.1 Then b=b & "Laengenziel <0.1% NICHT erreicht; Excel-Standard unveraendert."
    c="Excel-Kosinusradius: " & WEntryNumber(v(10),"mm") & vbCrLf
    c=c & "Korrigierter Kosinusradius: " & WEntryNumber(v(11),"mm") & vbCrLf
    c=c & "Kreisbogen-Dehnungsabschaetzung: " & WEntryNumber(v(12),"%") & vbCrLf
    c=c & "Excel-Dehnungsabschaetzung: " & WEntryNumber(v(13),"%") & vbCrLf
    c=c & "Korrigierte Kosinusabschaetzung: " & WEntryNumber(v(14),"%") & vbCrLf
    c=c & "Dehnung: stark vereinfachtes t/(2r)-Modell; keine Materialfreigabe oder Risssicherheitsaussage."
    WrinklePages=Array(a,b,c)
End Function

Function WrinkleRunChecked(ByRef ui)
    Dim raw,l1,l2,thickness,choice,values,pages,i
    WrinkleRunChecked=False
    raw=ui.Ask("Abgewickelte Laenge l1", "40")
    If IsEmpty(raw) Then Exit Function
    If Trim(CStr(raw))="" Then Exit Function
    l1=WParseDecimal(raw)
    raw=ui.Ask("Projizierte Breite l2", "30")
    If IsEmpty(raw) Then Exit Function
    If Trim(CStr(raw))="" Then Exit Function
    l2=WParseDecimal(raw)
    thickness=Empty
    choice=ui.ConfirmThickness()
    If choice=2 Then Exit Function
    If choice=6 Then
        raw=ui.Ask("Optionale Wanddicke", "2")
        If IsEmpty(raw) Then Exit Function
        If Trim(CStr(raw))="" Then Exit Function
        thickness=WParseDecimal(raw)
    ElseIf choice<>7 Then
        Err.Raise 5,"WrinkleEntry","Unbekannte Dialogantwort"
    End If
    values=WrinkleCalculate(l1,l2,thickness)
    If Not ui.ShowIllustrated(values, l1, l2, thickness) Then
        pages=WrinklePages(values,l1,l2)
        For i=0 To 2
            ui.ShowResult pages(i),i+1
        Next
    End If
    WrinkleRunChecked=True
End Function

Function WrinkleRun(ByRef ui)
    Dim success,number,description
    On Error Resume Next
    Err.Clear
    success=WrinkleRunChecked(ui)
    number=Err.Number: description=Err.Description
    On Error GoTo 0
    If number<>0 Then
        ui.ShowError description
        WrinkleRun=False
    Else
        WrinkleRun=success
    End If
End Function

Sub CATMain()
    Dim ui,success
    Set ui=New WrinkleDialogs
    success=WrinkleRun(ui)
End Sub
