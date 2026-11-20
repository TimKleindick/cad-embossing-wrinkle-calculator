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
    Public Sub ShowResult(ByVal text)
        MsgBox text,vbOKOnly+vbInformation,"Wrinkle Geometry - Source Preview"
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
        WEntryNumber=FormatNumber(value,2,-1,0,0) & " " & unit
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

Function WCosineNumber(ByVal value,ByVal unit)
    Dim exponent,mantissaText
    If value<=0 Or value>=0.01 Then
        WCosineNumber=WEntryNumber(value,unit)
        Exit Function
    End If
    exponent=Int(Log(value)/Log(10))
    mantissaText=FormatNumber(value/(10^exponent),2,-1,0,0)
    If CDbl(mantissaText)>=10 Then
        mantissaText=FormatNumber(1,2,-1,0,0)
        exponent=exponent+1
    End If
    WCosineNumber=mantissaText & "e" & CStr(exponent) & " " & unit
End Function

Function WCosineEstimateText(ByVal methodLabel,ByVal radius,ByVal strain)
    Dim radiusText,strainText
    If IsEmpty(radius) Then
        radiusText="unbounded (flat cosine)"
    Else
        radiusText=WCosineNumber(radius,"mm")
    End If
    If IsEmpty(strain) Then
        strainText="not calculated (no thickness)"
    Else
        strainText=WCosineNumber(strain,"%")
    End If
    WCosineEstimateText=methodLabel & ": R = " & radiusText & ", outer-fibre strain = " & strainText
End Function

Function WResultText(ByRef v,ByVal l1,ByVal l2,ByVal thickness)
    Dim report
    report="SOURCE PREVIEW - CATIA runtime and import untested" & vbCrLf
    report=report & "Undeformed wall length l1: " & WEntryNumber(l1,"mm") & vbCrLf
    report=report & "Deformed wall length l2 (neutral fibre): " & WEntryNumber(l2,"mm") & vbCrLf
    report=report & "Circular arc radius R: " & WEntryNumber(v(1),"mm") & vbCrLf
    report=report & "Height h: " & WEntryNumber(v(2),"mm") & vbCrLf
    report=report & "Flank angle: " & WEntryNumber(v(3),"deg") & vbCrLf
    report=report & "Wall thickness: " & WEntryNumber(thickness,"mm") & vbCrLf
    report=report & "l2 is the horizontal endpoint span of the neutral fibre." & vbCrLf
    report=report & WCosineEstimateText("Legacy estimate",v(10),v(13)) & vbCrLf
    report=report & WCosineEstimateText("Cosine curvature",v(11),v(14)) & vbCrLf
    report=report & "Both strains are model estimates." & vbCrLf
    report=report & "Fracture screening uses the legacy estimate in the illustrated report." & vbCrLf
    WResultText=report & "Actual cracking requires application-specific validation."
End Function

Function WrinkleRunChecked(ByRef ui)
    Dim raw,l1,l2,thickness,choice,values
    WrinkleRunChecked=False
    raw=ui.Ask("Undeformed wall length l1", "40")
    If IsEmpty(raw) Then Exit Function
    If Trim(CStr(raw))="" Then Exit Function
    l1=WParseDecimal(raw)
    raw=ui.Ask("Deformed wall length l2 (neutral fibre, horizontal endpoint span)", "30")
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
        Call ui.ShowResult(WResultText(values, l1, l2, thickness))
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
