' Standalone CATScript adapter. No CATVBA project, Excel, or installed helper required.
' The generator embeds the pure core and a local Windows Forms script.
Class WrinkleDialogs
    Public Function ReadInputs()
        Dim status, values
        status = WTryInputForm(values)
        If status = 0 Then
            ReadInputs = values
        ElseIf status = 2 Then
            ReadInputs = Empty
        Else
            ReadInputs = InputBox("Enter l1 [mm]; l2 [mm]; wall thickness [mm]; elongation at fracture A [%], in that order." & vbCrLf & _
                "For example: 40;30;2;24,5. Use a decimal point or comma without grouping." & vbCrLf & _
                "Leave either optional field blank (example: 40;30;;).", _
                "Wrinkle Geometry - Input", "40;30;2;")
        End If
    End Function
    Public Sub ShowResult(ByVal text)
        MsgBox text,vbOKOnly+vbInformation,"Wrinkle Geometry - Source Preview"
    End Sub
    Public Function ShowIllustrated(ByRef values, ByVal l1, ByVal l2, ByVal thickness, ByVal fractureElongation)
        Dim succeeded
        On Error Resume Next
        Err.Clear
        succeeded = WOpenResult(values, l1, l2, thickness, fractureElongation)
        ShowIllustrated = (Err.Number = 0 And succeeded = True)
        On Error GoTo 0
    End Function
    Public Sub ShowError(ByVal text)
        MsgBox "Error: " & text & vbCrLf & "No result. Run the macro again.", _
            vbOKOnly+vbExclamation,"Wrinkle Geometry - Check Input"
    End Sub
End Class

' The form returns only local numeric text. Input values never form part of the command line.
' Exit code 2 is a deliberate cancel, distinct from a blocked or unavailable form.
Function WTryInputForm(ByRef values)
    Dim fs, shell, folder, folderCreated, scriptPath, resultPath, exe, command
    Dim stream, resultCode
    values = Empty
    WTryInputForm = 1
    On Error Resume Next
    Err.Clear
    Set fs = CreateObject("Scripting.FileSystemObject")
    Set shell = CreateObject("WScript.Shell")
    If Err.Number = 0 Then
        folder = fs.BuildPath(fs.GetSpecialFolder(2).Path, "Wrinkle-input-" & fs.GetTempName)
        If Err.Number = 0 And InStr(folder, "%") = 0 Then
            Call fs.CreateFolder(folder)
            folderCreated = (Err.Number = 0)
        End If
        If folderCreated Then
            scriptPath = fs.BuildPath(folder, "input_form.ps1")
            resultPath = fs.BuildPath(folder, "values.txt")
            exe = shell.ExpandEnvironmentStrings("%SystemRoot%") & "\System32\WindowsPowerShell\v1.0\powershell.exe"
            Set stream = fs.CreateTextFile(scriptPath, False, False)
            If Err.Number = 0 Then
                stream.Write WInputFormScript()
                stream.Close
            End If
            If Err.Number = 0 And fs.FileExists(exe) And InStr(exe, "%") = 0 Then
                command = Chr(34) & exe & Chr(34) & _
                    " -NoProfile -NonInteractive -STA -File " & Chr(34) & scriptPath & Chr(34)
                resultCode = shell.Run(command, 0, True)
                If Err.Number = 0 Then
                    If resultCode = 2 Then
                        WTryInputForm = 2
                    ElseIf resultCode = 0 And fs.FileExists(resultPath) Then
                        Set stream = fs.OpenTextFile(resultPath, 1)
                        If Err.Number = 0 Then
                            values = stream.ReadAll
                            stream.Close
                            If Err.Number = 0 Then WTryInputForm = 0
                        End If
                    End If
                End If
            End If
            ' Delete only the files and the exact directory this invocation created.
            Err.Clear
            If fs.FileExists(resultPath) Then Call fs.DeleteFile(resultPath)
            If fs.FileExists(scriptPath) Then Call fs.DeleteFile(scriptPath)
            If fs.FolderExists(folder) Then Call fs.DeleteFolder(folder)
        End If
    End If
    Err.Clear
    On Error GoTo 0
End Function

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

Function WResultData(ByRef values, ByVal l1, ByVal l2, ByVal thickness, ByVal fractureElongation)
    Dim numbers(16), fit(200), i, phi, ordinate, reference
    For i = 0 To UBound(numbers)
        numbers(i) = WJsonNumber(values(i))
    Next
    phi = values(3) * WPI / 180
    For i = 0 To UBound(fit)
        ordinate = 0
        If Not IsEmpty(values(1)) Then ordinate = WrinkleY(l2 * (i / 200), l2, values(1), phi)
        fit(i) = WJsonNumber(ordinate)
    Next
    reference = ""
    If Not IsEmpty(fractureElongation) Then reference = ",""elongationAtFracture"":" & WJsonNumber(fractureElongation)
    WResultData = "{""l1"":" & WJsonNumber(l1) & ",""l2"":" & WJsonNumber(l2) & _
        ",""thickness"":" & WJsonNumber(thickness) & reference & ",""values"":[" & Join(numbers, ",") & _
        "],""fit"":[" & Join(fit, ",") & "]}"
End Function

Function WOpenResult(ByRef values, ByVal l1, ByVal l2, ByVal thickness, ByVal fractureElongation)
    Dim fs, shell, path, report, stream
    report = Replace(WResultTemplate(), "{{DATA}}", WResultData(values, l1, l2, thickness, fractureElongation))
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

Function WCosineEstimateText(ByVal radius,ByVal strain)
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
    WCosineEstimateText="Cosine curvature: R = " & radiusText & ", outer-fibre strain = " & strainText
End Function

Function WResultText(ByRef v,ByVal l1,ByVal l2,ByVal thickness, ByVal fractureElongation)
    Dim report
    report="SOURCE PREVIEW - CATIA runtime and import untested" & vbCrLf
    report=report & "Undeformed wall length l1: " & WEntryNumber(l1,"mm") & vbCrLf
    report=report & "Deformed wall length l2 (neutral fibre): " & WEntryNumber(l2,"mm") & vbCrLf
    report=report & "Circular arc radius R: " & WEntryNumber(v(1),"mm") & vbCrLf
    report=report & "Height h: " & WEntryNumber(v(2),"mm") & vbCrLf
    report=report & "Flank angle: " & WEntryNumber(v(3),"deg") & vbCrLf
    report=report & "Wall thickness: " & WEntryNumber(thickness,"mm") & vbCrLf
    report=report & "l2 is the horizontal endpoint span of the neutral fibre." & vbCrLf
    report=report & WCosineEstimateText(v(11),v(14)) & vbCrLf
    If Not IsEmpty(fractureElongation) Then
        report=report & "Elongation at fracture A: " & WEntryNumber(fractureElongation,"%") & _
            " (reference; not a cracking limit)" & vbCrLf
    End If
    WResultText=report & "The cosine bending estimate is not a crack prediction or material approval."
End Function

Function WrinkleRunChecked(ByRef ui)
    Dim raw,fields,l1,l2,thickness,fractureElongation,values
    WrinkleRunChecked=False
    raw=ui.ReadInputs()
    If IsEmpty(raw) Then Exit Function
    If Trim(CStr(raw))="" Then Exit Function
    fields=Split(CStr(raw), ";")
    If UBound(fields)<>3 Then Err.Raise 5,"WrinkleEntry","Enter l1; l2; wall thickness; elongation at fracture A"
    l1=WParseDecimal(fields(0))
    l2=WParseDecimal(fields(1))
    thickness=Empty
    If Trim(fields(2))<>"" Then thickness=WParseDecimal(fields(2))
    fractureElongation=Empty
    If Trim(fields(3))<>"" Then
        fractureElongation=WParseDecimal(fields(3))
        If fractureElongation<0 Or fractureElongation>1000000 Then
            Err.Raise 5,"WrinkleEntry","Elongation at fracture A must be between 0 and 1000000 %"
        End If
    End If
    values=WrinkleCalculate(l1,l2,thickness)
    If Not ui.ShowIllustrated(values, l1, l2, thickness, fractureElongation) Then
        Call ui.ShowResult(WResultText(values, l1, l2, thickness, fractureElongation))
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
