' This harness runs the actual generated macro orchestration, with controlled IO.
Class FixtureDialogs
    Public answers, position, thicknessChoice, prompts, outputs, errorText, illustrated, reportData
    Private Sub Class_Initialize()
        position=0
        prompts=""
        outputs=""
        errorText=""
        thicknessChoice=7
        illustrated=False
        reportData=""
    End Sub
    Public Function Ask(ByVal prompt,ByVal initial)
        prompts=prompts & prompt & vbCrLf
        Ask=answers(position)
        position=position+1
    End Function
    Public Function ConfirmThickness()
        ConfirmThickness=thicknessChoice
    End Function
    Public Sub ShowResult(ByVal text)
        outputs=outputs & text & vbCrLf
    End Sub
    Public Function ShowIllustrated(ByRef values, ByVal l1, ByVal l2, ByVal thickness)
        reportData = WResultData(values, l1, l2, thickness)
        ShowIllustrated = illustrated
    End Function
    Public Sub ShowError(ByVal text)
        errorText=text
    End Sub
End Class

Dim sample, value, caught, fake, success, localeId, previousLocale, restored, summary
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
    fake.answers=Array("40","30","2")
    fake.thicknessChoice=6
    success=WrinkleRun(fake)
    Assert success And fake.errorText="","successful entry workflow"
    Assert InStr(fake.prompts,"Undeformed wall length l1")>0,"l1 input label"
    Assert InStr(fake.prompts,"Deformed wall length l2 (neutral fibre, horizontal endpoint span)")>0,"l2 input label"
    If localeId=1033 Then summary="13.47 %" Else summary="13,47 %"
    Assert InStr(fake.outputs,"Calculated outer-fibre strain: " & summary)>0,"rounded calculated strain"
    Assert InStr(fake.outputs,"Undeformed wall length l1")>0,"l1 naming"
    Assert InStr(fake.outputs,"Deformed wall length l2 (neutral fibre)")>0,"l2 naming"
    Assert InStr(fake.outputs,"horizontal endpoint span")>0,"l2 definition"
    Assert InStr(fake.outputs,"Circular arc radius R")>0,"circular arc terminology"
    Assert InStr(fake.outputs,"Crack-risk comparison requires the illustrated report.")>0,"fracture comparison location"
    Assert InStr(fake.outputs,"cosine amplitude")=0 And InStr(fake.outputs,"Straight length")=0,"omit A and s"
    Assert InStr(fake.outputs,"Maximum vertical deviation")=0 And InStr(fake.outputs,"Corrected cosine")=0,"omit diagnostics"
    Set fake=New FixtureDialogs
    fake.answers=Array("40","30","2,5")
    fake.thicknessChoice=6
    fake.illustrated=True
    success=WrinkleRun(fake)
    Assert success And fake.outputs="" And fake.errorText="","illustrated report instead of text fallback"
    Assert InStr(fake.reportData,"{""l1"":40,""l2"":30,""thickness"":2.5,")=1,"report input values and JSON decimal"
    Assert InStr(fake.reportData,"""fit"":[0,")>0,"fitted curve starts at zero"
    Assert Right(fake.reportData,4)=",0]}","fitted curve ends at zero"
    Set fake=New FixtureDialogs
    fake.answers=Array("30","30")
    success=WrinkleRun(fake)
    Assert success And InStr(fake.outputs,"Not applicable")>0,"flat and thickness disabled"
    Assert InStr(fake.reportData,"""thickness"":null,""values"":[0,null,0,0,15,")>0,"flat report values and missing radius"
    For Each sample In Array(Array("","30"),Array("40",""),Array("40","30",""))
        Set fake=New FixtureDialogs
        fake.answers=sample
        If UBound(sample)=2 Then fake.thicknessChoice=6
        success=WrinkleRun(fake)
        Assert Not success And fake.outputs="" And fake.reportData="" And fake.errorText="","empty/cancel aborts cleanly"
    Next
    Set fake=New FixtureDialogs
    fake.answers=Array("40","30")
    fake.thicknessChoice=2
    success=WrinkleRun(fake)
    Assert Not success And fake.outputs="","confirmation cancel"
    For Each sample In Array(Array("29","30"),Array("text","30"),Array("40","30","-1"))
        Set fake=New FixtureDialogs
        fake.answers=sample
        If UBound(sample)=2 Then fake.thicknessChoice=6
        success=WrinkleRun(fake)
        Assert Not success And fake.outputs="" And fake.errorText<>"","invalid input must not show success"
    Next
    restored=SetLocale(previousLocale)
Next
WScript.Echo "PASS: actual generated CATScript parsing, illustrated report data, fallback, errors and cancellation under en-US/de-DE. CATIA host untested."
