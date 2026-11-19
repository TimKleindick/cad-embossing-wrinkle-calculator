' Native CATScript adapter. No CATVBA project, UserForm, Excel or external COM form.
' The generator embeds the unchanged pure core above this source.
Class WrinkleDialogs
    Public Function Ask(ByVal prompt,ByVal initial)
        Ask=InputBox(prompt & vbCrLf & "Lengths are in mm. Use a decimal point or comma without digit grouping. Leave blank or cancel to exit.", _
                     "Wrinkle Geometry - Source Preview",initial)
    End Function
    Public Function ConfirmThickness()
        ConfirmThickness=MsgBox("Estimate strain from wall thickness?" & vbCrLf & _
            "Simplified t/(2r) estimate. Material approval and crack safety are outside its scope.", _
            vbYesNoCancel+vbQuestion,"Wrinkle Geometry - Source Preview")
    End Function
    Public Sub ShowResult(ByVal text,ByVal page)
        MsgBox text,vbOKOnly+vbInformation,"Wrinkle Geometry - Source Preview - " & page & "/3"
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
        MsgBox "Error: " & text & vbCrLf & "No result. Run the macro again.", _
            vbOKOnly+vbExclamation,"Wrinkle Geometry - Check Input"
    End Sub
End Class

Function WParseDecimal(ByVal text)
    Dim i,ch,value,factor,sign,seenSeparator,digitsBefore,digitsAfter
    text=Trim(CStr(text))
    If Len(text)=0 Or Len(text)>32 Then Err.Raise 5,"WrinkleEntry","Enter a number with a decimal point or comma"
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
            Err.Raise 5,"WrinkleEntry","Use one decimal point or comma without digit grouping or exponents"
        End If
    Next
    If digitsBefore=0 Or (seenSeparator And digitsAfter=0) Then Err.Raise 5,"WrinkleEntry","Incomplete number"
    WParseDecimal=sign*value
End Function

Function WEntryNumber(ByVal value,ByVal unit)
    If IsEmpty(value) Then
        WEntryNumber="Not applicable or not provided"
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
    path = fs.BuildPath(fs.GetSpecialFolder(2).Path, "Wrinkle-geometry-" & fs.GetTempName & ".html")
    Set stream = fs.CreateTextFile(path, False, False)
    stream.Write report
    stream.Close
    Call shell.ShellExecute(path, "", "", "open", 1)
    WOpenResult = True
End Function

Function WrinklePages(ByRef v,ByVal l1,ByVal l2)
    Dim a,b,c
    a="SOURCE PREVIEW - CATIA runtime and import untested" & vbCrLf
    a=a & "Excel method with 1,000 segments and no fitted-length constraint." & vbCrLf
    a=a & "l1 (developed target length along the cosine): " & l1 & " mm" & vbCrLf
    a=a & "l2 (projected width between endpoints): " & l2 & " mm" & vbCrLf
    a=a & "A (cosine amplitude, crest at 2A): " & WEntryNumber(v(0),"mm") & vbCrLf
    a=a & "R (common radius of the three arcs): " & WEntryNumber(v(1),"mm") & vbCrLf
    a=a & "Height h: " & WEntryNumber(v(2),"mm") & vbCrLf & "Flank angle: " & WEntryNumber(v(3),"deg") & vbCrLf
    a=a & "Straight length per side: " & WEntryNumber(v(4),"mm")
    b="Fitted polyline length: " & WEntryNumber(v(5),"mm") & vbCrLf
    b=b & "Analytic fitted length: " & WEntryNumber(v(6),"mm") & vbCrLf
    b=b & "Polyline length deviation: " & WEntryNumber(v(7),"%") & vbCrLf
    b=b & "RMS vertical profile deviation: " & WEntryNumber(v(8),"mm") & vbCrLf
    b=b & "Maximum vertical deviation at sample points: " & WEntryNumber(v(9),"mm") & vbCrLf
    If Abs(v(7))>=0.1 Then b=b & "Length deviation reaches or exceeds 0.1%."
    c="Cosine radius using the Excel formula: " & WEntryNumber(v(10),"mm") & vbCrLf
    c=c & "Corrected cosine radius: " & WEntryNumber(v(11),"mm") & vbCrLf
    c=c & "Circular arc strain estimate: " & WEntryNumber(v(12),"%") & vbCrLf
    c=c & "Cosine strain using the Excel radius: " & WEntryNumber(v(13),"%") & vbCrLf
    c=c & "Cosine strain using the corrected radius: " & WEntryNumber(v(14),"%") & vbCrLf
    c=c & "Simplified t/(2r) estimate. Material approval and crack safety are outside its scope."
    WrinklePages=Array(a,b,c)
End Function

Function WrinkleRunChecked(ByRef ui)
    Dim raw,l1,l2,thickness,choice,values,pages,i
    WrinkleRunChecked=False
    raw=ui.Ask("Developed target length l1", "40")
    If IsEmpty(raw) Then Exit Function
    If Trim(CStr(raw))="" Then Exit Function
    l1=WParseDecimal(raw)
    raw=ui.Ask("Projected width l2", "30")
    If IsEmpty(raw) Then Exit Function
    If Trim(CStr(raw))="" Then Exit Function
    l2=WParseDecimal(raw)
    thickness=Empty
    choice=ui.ConfirmThickness()
    If choice=2 Then Exit Function
    If choice=6 Then
        raw=ui.Ask("Optional wall thickness", "2")
        If IsEmpty(raw) Then Exit Function
        If Trim(CStr(raw))="" Then Exit Function
        thickness=WParseDecimal(raw)
    ElseIf choice<>7 Then
        Err.Raise 5,"WrinkleEntry","Unexpected answer"
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
