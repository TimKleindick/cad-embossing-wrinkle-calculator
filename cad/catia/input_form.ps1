# Embedded in the standalone CATScript. All values and generated output stay local.
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[System.Windows.Forms.Application]::EnableVisualStyles()
$form = New-Object System.Windows.Forms.Form
$form.Text = 'Wrinkle Geometry - Input'
$form.ClientSize = New-Object System.Drawing.Size -ArgumentList 770, 252
$form.AutoScaleMode = 'Dpi'
$form.FormBorderStyle = 'FixedDialog'
$form.StartPosition = 'CenterScreen'
$form.MaximizeBox = $false
$form.MinimizeBox = $false
$form.TopMost = $true

function Add-Label($text, $x, $y, $width, $height) {
    $label = New-Object System.Windows.Forms.Label
    $label.Text = $text
    $label.SetBounds($x, $y, $width, $height)
    $form.Controls.Add($label)
    return $label
}

$labels = @('Undeformed wall length l1 [mm]',
            'Deformed wall length l2 (neutral fibre) [mm]',
            'Wall thickness [mm] (optional)',
            'Elongation at fracture A [%] (optional)')
$defaults = @('40', '30', '2', '')
$entries = @(
    for ($i = 0; $i -lt $labels.Count; $i++) {
        $y = 15 + 34 * $i
        $null = Add-Label $labels[$i] 14 ($y + 3) 330 25
        $entry = New-Object System.Windows.Forms.TextBox
        $entry.Name = "Input$i"
        $entry.AccessibleName = $labels[$i]
        $entry.Text = $defaults[$i]
        $entry.MaxLength = 32
        $entry.SetBounds(350, $y, 145, 25)
        $entry.TabIndex = $i
        $form.Controls.Add($entry)
        $entry
    }
)
# The generator supplies exactly the same dimension paths as the NX dialog.
$inputSketch = '{{INPUT_SKETCH}}' | ConvertFrom-Json
$sketchBox = New-Object System.Windows.Forms.PictureBox
$sketchBox.Name = 'InputSketch'
$sketchBox.AccessibleName = 'Input sketch: L1 follows the profile, L2 is the chord, and t is the wall thickness'
$sketchBox.BackColor = [System.Drawing.SystemColors]::Window
$sketchBox.SetBounds(513, 12, 243, 122)
$form.Controls.Add($sketchBox)
$sketchBox.Add_Paint({
    param($sender, $event)
    $g = $event.Graphics
    $scale = [Math]::Min($sender.Width / $inputSketch.width, $sender.Height / $inputSketch.height)
    $g.TranslateTransform([single](($sender.Width - $inputSketch.width * $scale) / 2),
                          [single](($sender.Height - $inputSketch.height * $scale) / 2))
    $g.ScaleTransform([single]$scale, [single]$scale)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    foreach ($pathGroup in $inputSketch.paths.PSObject.Properties) {
        foreach ($path in $pathGroup.Value) {
            for ($i = 1; $i -lt $path.Count; $i++) {
                $a = $path[$i - 1]
                $b = $path[$i]
                $g.DrawLine([System.Drawing.SystemPens]::WindowText,
                            [single]$a[0], [single]$a[1], [single]$b[0], [single]$b[1])
            }
        }
    }
    foreach ($label in $inputSketch.labels.PSObject.Properties) {
        $g.DrawString($label.Name, $form.Font, [System.Drawing.SystemBrushes]::WindowText,
                      [single]$label.Value[0], [single]$label.Value[1])
    }
})
$legend = "L1 = developed material length`r`nL2 = projected endpoint length (chord)`r`nt = wall thickness`r`nA [%] = tensile elongation at fracture`r`nSchematic, not to scale"
$null = Add-Label $legend 513 139 243 74
$null = Add-Label 'Use a decimal point or comma. Leave optional fields blank if not provided.' 14 151 481 24
$errorLabel = Add-Label '' 14 174 481 38
$errorLabel.ForeColor = [System.Drawing.Color]::DarkRed
$calculate = New-Object System.Windows.Forms.Button
$calculate.Text = 'Calculate'
$calculate.SetBounds(295, 214, 95, 27)
$calculate.TabIndex = $entries.Count
$form.Controls.Add($calculate)
$form.AcceptButton = $calculate
$cancel = New-Object System.Windows.Forms.Button
$cancel.Text = 'Cancel'
$cancel.SetBounds(400, 214, 95, 27)
$cancel.TabIndex = $entries.Count + 1
$cancel.DialogResult = 'Cancel'
$form.Controls.Add($cancel)
$form.CancelButton = $cancel

function Read-Value($control, $minimum, $optional, $name, $unit) {
    $value = $control.Text.Trim()
    if ($optional -and $value.Length -eq 0) { return $null }
    if ($value -notmatch '^[+-]?[0-9]+([.,][0-9]+)?$') {
        throw "Enter $name as a decimal number without grouping."
    }
    $number = [double]::Parse($value.Replace(',', '.'), [Globalization.CultureInfo]::InvariantCulture)
    if ($number -lt $minimum -or $number -gt 1000000) {
        throw "$name must be between $minimum and 1000000 $unit."
    }
    return $number
}

$calculate.Add_Click({
    try {
        $l1 = Read-Value $entries[0] 0.001 $false 'l1' 'mm'
        $l2 = Read-Value $entries[1] 0.001 $false 'l2' 'mm'
        $null = Read-Value $entries[2] 0 $true 'wall thickness' 'mm'
        $null = Read-Value $entries[3] 0 $true 'elongation at fracture A' '%'
        if ($l1 -lt $l2 -or $l1 -gt 2 * $l2) {
            throw 'Lengths must satisfy l2 <= l1 <= 2*l2.'
        }
        $values = @($entries | ForEach-Object { $_.Text.Trim() })
        $resultPath = Join-Path $PSScriptRoot 'values.txt'
        [IO.File]::WriteAllText($resultPath, ($values -join ';'), [Text.Encoding]::ASCII)
        $form.DialogResult = 'OK'
    } catch {
        $errorLabel.Text = $_.Exception.Message
    }
})

try {
    if ($form.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) { exit 0 }
    exit 2
} finally {
    $form.Dispose()
}
