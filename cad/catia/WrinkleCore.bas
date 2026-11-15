Attribute VB_Name = "WrinkleCore"
Option Explicit
' Pure VBA source, deliberately also executable by Windows VBScript tests.
' No CATIA/Excel/COM objects. Units: mm, degrees, percent. See docs/MATHEMATICS.md.
Const WPI = 3.141592653589793
Const WN = 1000

Sub WNumber(ByVal value, ByVal name, ByVal lo, ByVal hi)
    If IsEmpty(value) Or IsNull(value) Or VarType(value) = 8 Or VarType(value) = 11 Then
        Err.Raise 5, "WrinkleCore", name & " must be a number"
    End If
    If Not IsNumeric(value) Then Err.Raise 5, "WrinkleCore", name & " must be a number"
    If value < lo Or value > hi Then Err.Raise 5, "WrinkleCore", name & " outside supported range"
End Sub

Function WAmplitude(ByVal ratio)
    Dim dy(1000), i, old, y, lo, hi, mid, total, j
    old = 0
    For i = 1 To WN
        y = 2 * Sin(WPI * i / WN) ^ 2
        dy(i) = y - old
        old = y
    Next
    lo = 0
    hi = ratio / 4
    For j = 1 To 64
        mid = (lo + hi) / 2
        total = 0
        For i = 1 To WN
            total = total + Sqr((1 / WN) ^ 2 + (mid * dy(i)) ^ 2)
        Next
        If total < ratio Then
            lo = mid
        Else
            hi = mid
        End If
    Next
    WAmplitude = (lo + hi) / 2
End Function

Function WOrdinate(ByVal u, ByVal r, ByVal first, ByVal second, ByVal h, ByVal slope, ByVal startY)
    Dim d, disc
    If u < first Then
        disc = r * r - u * u
        If disc < 0 Then disc = 0
        WOrdinate = u * u / (r + Sqr(disc))
    ElseIf u <= second Then
        WOrdinate = startY + (u - first) * slope
    Else
        d = 0.5 - u
        disc = r * r - d * d
        If disc < 0 Then disc = 0
        WOrdinate = h - d * d / (r + Sqr(disc))
    End If
End Function

Function WrinkleY(ByVal x, ByVal span, ByVal radius, ByVal phi)
    Dim q, r, u, h, first
    q = 4 * radius / span * Sin(phi)
    If x < 0 Or x > span Or q <= 0 Or q > 1 Or phi <= 0 Or phi >= WPI / 2 Then
        Err.Raise 5, "WrinkleCore", "invalid profile parameters"
    End If
    r = radius / span
    u = x / span
    If u > 0.5 Then u = 1 - u
    first = q / 4
    h = 0.5 * (1 - q) * Tan(phi) + 0.5 * q * Tan(phi / 2)
    WrinkleY = span * WOrdinate(u, r, first, 0.5 - first, h, Tan(phi), 2 * r * Sin(phi / 2) ^ 2)
End Function

Function WObjective(ByVal q, ByVal z, ByVal basePhi, ByRef targets)
    Dim phi, r, first, second, h, slope, startY, i, diff, total, weight
    phi = z * basePhi
    If q <= 0.00000001 Or q >= 0.99999999 Or phi <= 0 Or phi >= WPI / 2 - 0.000001 Then
        WObjective = 1E100
        Exit Function
    End If
    r = q / (4 * Sin(phi))
    first = q / 4
    second = 0.5 - first
    h = 0.5 * (1 - q) * Tan(phi) + 0.5 * q * Tan(phi / 2)
    slope = Tan(phi)
    startY = 2 * r * Sin(phi / 2) ^ 2
    total = 0
    For i = 0 To WN / 2
        diff = WOrdinate(i / WN, r, first, second, h, slope, startY) - targets(i)
        weight = 2
        If i = WN / 2 Then weight = 1
        total = total + weight * diff * diff
    Next
    WObjective = total
End Function

Function WSimplex(ByVal seed, ByVal basePhi, ByRef targets)
    Dim p(2,1), f(2), i, j, k, tmp, delta, iteration
    Dim cq, cz, rq, rz, fr, eq, ez, fe, tq, tz, fc, outside, threshold
    p(0,0) = seed: p(0,1) = 1
    p(1,0) = seed + 0.05: p(1,1) = 1
    p(2,0) = seed: p(2,1) = 1.1
    For i = 0 To 2
        f(i) = WObjective(p(i,0), p(i,1), basePhi, targets)
    Next
    For iteration = 0 To 399
        For i = 0 To 1
            For j = i + 1 To 2
                If f(j) < f(i) Then
                    tmp = f(i): f(i) = f(j): f(j) = tmp
                    For k = 0 To 1
                        tmp = p(i,k): p(i,k) = p(j,k): p(j,k) = tmp
                    Next
                End If
            Next
        Next
        delta = 0
        For i = 1 To 2
            For k = 0 To 1
                If Abs(p(i,k) - p(0,k)) > delta Then delta = Abs(p(i,k) - p(0,k))
            Next
        Next
        If delta < 0.000000001 Then
            WSimplex = Array(p(0,0), p(0,1), f(0), iteration)
            Exit Function
        End If
        cq = (p(0,0) + p(1,0)) / 2
        cz = (p(0,1) + p(1,1)) / 2
        rq = 2 * cq - p(2,0): rz = 2 * cz - p(2,1)
        fr = WObjective(rq, rz, basePhi, targets)
        If fr < f(0) Then
            eq = cq + 2 * (rq - cq): ez = cz + 2 * (rz - cz)
            fe = WObjective(eq, ez, basePhi, targets)
            If fe < fr Then
                p(2,0) = eq: p(2,1) = ez: f(2) = fe
            Else
                p(2,0) = rq: p(2,1) = rz: f(2) = fr
            End If
        ElseIf fr < f(1) Then
            p(2,0) = rq: p(2,1) = rz: f(2) = fr
        Else
            outside = (fr < f(2))
            tq = p(2,0): tz = p(2,1): threshold = f(2)
            If outside Then
                tq = rq: tz = rz: threshold = fr
            End If
            tq = (cq + tq) / 2: tz = (cz + tz) / 2
            fc = WObjective(tq, tz, basePhi, targets)
            If fc < threshold Then
                p(2,0) = tq: p(2,1) = tz: f(2) = fc
            Else
                For i = 1 To 2
                    For k = 0 To 1
                        p(i,k) = (p(0,k) + p(i,k)) / 2
                    Next
                    f(i) = WObjective(p(i,0), p(i,1), basePhi, targets)
                Next
            End If
        End If
    Next
    Err.Raise 5, "WrinkleCore", "form fit did not converge; no result released"
End Function

Function WrinkleCalculate(ByVal l1, ByVal l2, ByVal thickness)
    Dim a, basePhi, targets(500), i, best, other, q, phi, r, first, h, s
    Dim y, old, polygon, analytic, maxError, rexcel, corrected, arcStrain, excelStrain, correctedStrain
    WNumber l1, "l1", 0.001, 1000000
    WNumber l2, "l2", 0.001, 1000000
    If l1 < l2 Or l1 > 2 * l2 Then Err.Raise 5, "WrinkleCore", "requires l2 <= l1 <= 2*l2"
    If Not IsEmpty(thickness) Then WNumber thickness, "thickness", 0, 1000000
    If l1 = l2 Then
        arcStrain = Empty
        If Not IsEmpty(thickness) Then arcStrain = 0
        WrinkleCalculate = Array(0, Empty, 0, 0, l2 / 2, l2, l2, 0, 0, 0, Empty, Empty, arcStrain, arcStrain, arcStrain, 0, WN)
        Exit Function
    End If
    a = WAmplitude(l1 / l2)
    basePhi = Atn(2 * WPI * a)
    For i = 0 To WN / 2
        targets(i) = 2 * a * Sin(WPI * i / WN) ^ 2
    Next
    best = WSimplex(0.3, basePhi, targets)
    other = WSimplex(0.7, basePhi, targets)
    If other(2) < best(2) Then best = other
    q = best(0): phi = best(1) * basePhi
    If q < 0.000001 Or q > 0.999999 Then Err.Raise 5, "WrinkleCore", "degenerate fit boundary"
    r = q / (4 * Sin(phi))
    first = q / 4
    h = 0.5 * (1 - q) * Tan(phi) + 0.5 * q * Tan(phi / 2)
    s = (0.5 - 2 * r * Sin(phi)) / Cos(phi)
    polygon = 0: old = 0: maxError = 0
    For i = 0 To WN / 2
        y = WOrdinate(i / WN, r, first, 0.5 - first, h, Tan(phi), 2 * r * Sin(phi / 2) ^ 2)
        If Abs(y - targets(i)) > maxError Then maxError = Abs(y - targets(i))
        If i > 0 Then polygon = polygon + 2 * Sqr((1 / WN) ^ 2 + (y - old) ^ 2)
        old = y
    Next
    analytic = 4 * r * phi + 2 * s
    rexcel = 1 / (2 * WPI * WPI * a): corrected = rexcel / 2
    arcStrain = Empty: excelStrain = Empty: correctedStrain = Empty
    If Not IsEmpty(thickness) Then
        arcStrain = 100 * (thickness / l2) / (2 * r)
        excelStrain = 100 * (thickness / l2) / (2 * rexcel)
        correctedStrain = 100 * (thickness / l2) / (2 * corrected)
    End If
    WrinkleCalculate = Array(a * l2, r * l2, h * l2, phi * 180 / WPI, s * l2, polygon * l2, analytic * l2, _
        (polygon * l2 / l1 - 1) * 100, Sqr(best(2) / (WN + 1)) * l2, maxError * l2, rexcel * l2, corrected * l2, _
        arcStrain, excelStrain, correctedStrain, best(2) * l2 * l2, WN)
End Function
