' Executed with the actual WrinkleCore.bas source, not a rewritten implementation.
Dim fs, fixture, row, cols, values, k, expected, tolerance, count, bad, errNumber
Dim fixtureLocale, restoredLocale
fixtureLocale = SetLocale(1033)
' CSV decimals are invariant; test runner also starts this harness under de-DE.
Set fs = CreateObject("Scripting.FileSystemObject")
Set fixture = fs.OpenTextFile(WScript.Arguments(0), 1)
fixture.ReadLine
count = 0
Do Until fixture.AtEndOfStream
    row = fixture.ReadLine
    If Len(row) > 0 Then
        cols = Split(row, ",")
        values = WrinkleCalculate(CDbl(cols(1)), CDbl(cols(2)), CDbl(cols(3)))
        For k = 0 To 6
            If cols(k + 4) = "" Then
                Assert IsEmpty(values(k)), cols(0) & " flat radius must be undefined"
            Else
                expected = CDbl(cols(k + 4))
                tolerance = 0.000001 * CDbl(cols(2)) / 30
                If k = 3 Then tolerance = 0.00001
                Assert Abs(values(k) - expected) < tolerance, cols(0) & " field " & k & " got " & values(k)
            End If
        Next
        count = count + 1
    End If
Loop
fixture.Close
values = WrinkleCalculate(40, 30, 2)
Assert values(7) > 0.4 And values(7) < 0.5, "default must retain Excel fit length error"
Assert Abs(values(13) - 13.465240047) < 0.00001, "Excel strain"
Assert Abs(values(14) - 26.930480093) < 0.00001, "corrected strain"
Assert Abs(values(12) - 19.871805437) < 0.00001, "arc strain"
Assert values(8) > 0.09 And values(9) > 0.18, "shape residuals"
Assert Abs(values(10) - 2 * values(11)) < 0.0000001, "radius conventions"
Dim scaled, nearFlat, edgeCase, noneThickness, flat, rad, phi, xJoin, eps, yl, yr, yc
scaled = WrinkleCalculate(400, 300, 20)
Assert Abs(scaled(0) - values(0) * 10) < 0.000001, "amplitude scaling"
Assert Abs(scaled(1) - values(1) * 10) < 0.000001, "radius scaling"
Assert Abs(scaled(7) - values(7)) < 0.000001, "relative error scaling"
nearFlat = WrinkleCalculate(30.00003, 30, Empty)
edgeCase = WrinkleCalculate(60, 30, Empty)
noneThickness = WrinkleCalculate(40, 30, Empty)
Assert nearFlat(0) > 0 And edgeCase(4) > 0, "near-flat and envelope end"
Assert IsEmpty(noneThickness(12)), "missing thickness has no strain estimate"
flat = WrinkleCalculate(30, 30, 2)
Assert IsEmpty(flat(1)) And IsEmpty(flat(10)) And flat(12) = 0, "flat semantics"
rad = values(1)
phi = values(3) * 3.141592653589793 / 180
xJoin = rad * Sin(phi)
eps = 0.00001
yc = WrinkleY(xJoin, 30, rad, phi)
yl = (yc - WrinkleY(xJoin - eps, 30, rad, phi)) / eps
yr = (WrinkleY(xJoin + eps, 30, rad, phi) - yc) / eps
Assert Abs(yl - Tan(phi)) < 0.00001 And Abs(yl - yr) < 0.00001, "tangency"
For k = 0 To 30
    Assert Abs(WrinkleY(k, 30, rad, phi) - WrinkleY(30-k, 30, rad, phi)) < 0.0000001, "symmetry"
Next
For Each bad In Array(Array(29,30,Empty), Array(0,0,Empty), Array(-1,1,Empty), Array(61,30,Empty), Array(40,30,-1), Array(True,1,Empty), Array("40",30,Empty))
    On Error Resume Next
    Err.Clear
    values = WrinkleCalculate(bad(0), bad(1), bad(2))
    errNumber = Err.Number
    On Error GoTo 0
    Assert errNumber <> 0, "invalid input must fail"
Next
restoredLocale = SetLocale(fixtureLocale)
WScript.Echo "PASS: " & count & " shared references; scaling, flat, near-flat, envelope, input, strain, form and tangency checks."
WScript.Echo "VBScript execution only: VBA compilation/CATIA runtime/UI/import/license NOT tested."

Sub Assert(ByVal condition, ByVal message)
    If Not condition Then
        WScript.Echo "FAIL: " & message
        WScript.Quit 1
    End If
End Sub
