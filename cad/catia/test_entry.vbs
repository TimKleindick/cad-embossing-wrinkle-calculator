' This harness runs the actual generated macro orchestration, with controlled IO.
Class FixtureDialogs
    Public answer, inputCalls, outputs, errorText, illustrated, reportData
    Private Sub Class_Initialize()
        inputCalls=0
        outputs=""
        errorText=""
        illustrated=False
        reportData=""
    End Sub
    Public Function ReadInputs()
        inputCalls=inputCalls+1
        ReadInputs=answer
    End Function
    Public Sub ShowResult(ByVal text)
        outputs=outputs & text & vbCrLf
    End Sub
    Public Function ShowIllustrated(ByRef values, ByVal l1, ByVal l2, ByVal thickness, ByVal fractureElongation)
        reportData = WResultData(values, l1, l2, thickness, fractureElongation)
        ShowIllustrated = illustrated
    End Function
    Public Sub ShowError(ByVal text)
        errorText=text
    End Sub
End Class

Sub AssertCosineText(ByVal textResult, ByVal exactRadius, ByVal exactStrain)
    Assert InStr(textResult,"Cosine curvature: R = " & exactRadius & ", outer-fibre strain = " & exactStrain)>0,"curvature method"
    Assert InStr(textResult,"Legacy estimate")=0,"only cosine curvature is shown"
    Assert InStr(textResult,"Fracture screening")=0,"no fracture screening"
    Assert InStr(textResult,"not a crack prediction")>0,"validation caveat"
    Assert Len(textResult)<1024,"compact message box fallback"
End Sub

Dim sample, value, caught, fake, success, localeId, previousLocale, restored
Dim exactRadius, exactStrain, zeroStrain, flatRadius, missingStrain, decimalPoint
flatRadius="unbounded (flat cosine)"
missingStrain="not calculated (no thickness)"
For Each localeId In Array(1033,1031)
    previousLocale=SetLocale(localeId)
    Assert Abs(WParseDecimal("6,25")-6.25)<0.000001,"comma decimal"
    Assert Abs(WParseDecimal("6.25")-6.25)<0.000001,"dot decimal"
    For Each sample In Array("", " ", "1,234.5", "1.234,5", "1 000", "1e3", "nan", "inf", ".5", "1.", "--1", "2mm")
        On Error Resume Next
        Err.Clear
        value=WParseDecimal(sample)
        caught=Err.Number
        On Error GoTo 0
        Assert caught<>0,"invalid decimal " & sample
    Next
    Set fake=New FixtureDialogs
    fake.answer="40;30;2;"
    success=WrinkleRun(fake)
    Assert success And fake.errorText="","successful entry workflow"
    Assert fake.inputCalls=1,"all dimensions requested together exactly once"
    If localeId=1033 Then
        exactRadius="3.71 mm": exactStrain="26.93 %": zeroStrain="0.00 %"
    Else
        exactRadius="3,71 mm": exactStrain="26,93 %": zeroStrain="0,00 %"
    End If
    Call AssertCosineText(fake.outputs,exactRadius,exactStrain)
    Assert InStr(fake.outputs,"Undeformed wall length l1")>0,"l1 naming"
    Assert InStr(fake.outputs,"Deformed wall length l2 (neutral fibre)")>0,"l2 naming"
    Assert InStr(fake.outputs,"horizontal endpoint span")>0,"l2 definition"
    Assert InStr(fake.outputs,"Circular arc radius R")>0,"circular arc terminology"
    Assert InStr(fake.outputs,"cosine amplitude")=0 And InStr(fake.outputs,"Straight length")=0,"omit A and s"
    Assert InStr(fake.outputs,"Maximum vertical deviation")=0 And InStr(fake.outputs,"Corrected cosine")=0,"omit diagnostics"
    Set fake=New FixtureDialogs
    fake.answer="0.002;0.001;0.000000001;"
    success=WrinkleRun(fake)
    Assert success,"small positive radius and strain"
    If localeId=1033 Then
        Call AssertCosineText(fake.outputs,"6.12e-5 mm","8.17e-4 %")
    Else
        Call AssertCosineText(fake.outputs,"6,12e-5 mm","8,17e-4 %")
    End If
    Set fake=New FixtureDialogs
    fake.answer="40;30;2,5;24,5"
    fake.illustrated=True
    success=WrinkleRun(fake)
    Assert success And fake.outputs="" And fake.errorText="","illustrated report instead of text fallback"
    Assert InStr(fake.reportData,"{""l1"":40,""l2"":30,""thickness"":2.5,""elongationAtFracture"":24.5,")=1,"report input values and JSON decimal"
    Assert InStr(fake.reportData,"""fit"":[0,")>0,"fitted curve starts at zero"
    Assert Right(fake.reportData,4)=",0]}","fitted curve ends at zero"
    Set fake=New FixtureDialogs
    fake.answer="40;30;2;24,5"
    success=WrinkleRun(fake)
    Assert success,"reference value accepted without affecting geometry"
    Assert InStr(fake.outputs,"Elongation at fracture A: ")>0 And InStr(fake.outputs,"not a cracking limit")>0,"reference caveat"
    decimalPoint = Mid(CStr(0.5), 2, 1)
    Assert InStr(fake.outputs,"+2" & decimalPoint & "43 percentage points")>0,"positive strain minus A"
    Assert InStr(fake.outputs,"Potential cracking risk under this simplified check")>0,"exceeded reference flags potential risk"
    Assert InStr(WStrainComparison(25,25),"0" & decimalPoint & "00 percentage points")>0,"equal reference"
    Assert InStr(WStrainComparison(25,26),"-1" & decimalPoint & "00 percentage points")>0,"negative strain minus A"
    Assert InStr(WStrainComparison(25,26),"at or below the entered reference")>0,"non-exceeded reference"
    Assert WStrainComparison(Empty,24.5)="" And WStrainComparison(25,Empty)="","missing input skips comparison"
    Call AssertCosineText(fake.outputs,exactRadius,exactStrain)
    Set fake=New FixtureDialogs
    fake.answer="30;30;;"
    success=WrinkleRun(fake)
    Assert success And InStr(fake.outputs,"Not applicable")>0,"flat and thickness disabled"
    Call AssertCosineText(fake.outputs,flatRadius,missingStrain)
    Assert InStr(fake.reportData,"""thickness"":null,""values"":[0,null,0,0,15,")>0,"flat report values and missing radius"
    Set fake=New FixtureDialogs
    fake.answer="30;30;2;"
    success=WrinkleRun(fake)
    Assert success,"flat with thickness"
    Call AssertCosineText(fake.outputs,flatRadius,zeroStrain)
    For Each sample In Array(Empty, "", " ")
        Set fake=New FixtureDialogs
        fake.answer=sample
        success=WrinkleRun(fake)
        Assert Not success And fake.outputs="" And fake.reportData="" And fake.errorText="","empty/cancel aborts cleanly"
        Assert fake.inputCalls=1,"cancel does not reopen the input window"
    Next
    For Each sample In Array("29;30;;", "text;30;;", "40;30;-1;", "40;30", "40;30;2;extra", ";30;2;", "40;;2;", "40;30;2;-1")
        Set fake=New FixtureDialogs
        fake.answer=sample
        success=WrinkleRun(fake)
        Assert Not success And fake.outputs="" And fake.errorText<>"","invalid input must not show success"
    Next
    restored=SetLocale(previousLocale)
Next
WScript.Echo "PASS: actual generated CATScript parsing, illustrated report data, fallback, errors and cancellation under en-US/de-DE. CATIA host untested."
