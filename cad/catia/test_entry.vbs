' This harness runs the actual generated macro orchestration, with controlled IO.
Class FixtureDialogs
    Public answers, position, thicknessChoice, outputs, errorText
    Private Sub Class_Initialize()
        position=0
        outputs=""
        errorText=""
        thicknessChoice=7
    End Sub
    Public Function Ask(ByVal prompt,ByVal initial)
        Ask=answers(position)
        position=position+1
    End Function
    Public Function ConfirmThickness()
        ConfirmThickness=thicknessChoice
    End Function
    Public Sub ShowResult(ByVal text,ByVal page)
        outputs=outputs & text & vbCrLf
    End Sub
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
    If localeId=1033 Then summary="6.139413268" Else summary="6,139413268"
    Assert InStr(fake.outputs,summary)>0,"calculated amplitude in visible output"
    Assert InStr(fake.outputs,"0.434593")>0 Or InStr(fake.outputs,"0,434593")>0,"length error visible"
    Assert InStr(fake.outputs,"13.465240")>0 Or InStr(fake.outputs,"13,465240")>0,"Excel strain visible"
    Assert InStr(fake.outputs,"NICHT erreicht")>0,"length target status"
    Set fake=New FixtureDialogs
    fake.answers=Array("30","30")
    success=WrinkleRun(fake)
    Assert success And InStr(fake.outputs,"entfaellt")>0,"flat and thickness disabled"
    For Each sample In Array(Array("","30"),Array("40",""),Array("40","30",""))
        Set fake=New FixtureDialogs
        fake.answers=sample
        If UBound(sample)=2 Then fake.thicknessChoice=6
        success=WrinkleRun(fake)
        Assert Not success And fake.outputs="" And fake.errorText="","empty/cancel aborts cleanly"
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
WScript.Echo "PASS: actual generated CATScript parsing, result pages, errors and cancellation under en-US/de-DE. CATIA host untested."
