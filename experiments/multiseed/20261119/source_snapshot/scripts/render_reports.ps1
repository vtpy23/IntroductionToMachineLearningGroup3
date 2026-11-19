param([string]$GroupId='03')
$ErrorActionPreference = 'Stop'
$projectPath = Split-Path -Parent $PSScriptRoot
$outputPath = Join-Path $projectPath 'reports/output'
$buildPath = Join-Path $projectPath 'reports/.build'
New-Item -ItemType Directory -Force -Path $buildPath | Out-Null
$wasRunning = [bool](Get-Process POWERPNT -ErrorAction SilentlyContinue)
$application = New-Object -ComObject PowerPoint.Application
$checks = @()
try {
    foreach ($name in @($GroupId, "$GroupId-poster-draft")) {
        $file = Join-Path $outputPath "$name.pptx"
        if (!(Test-Path -LiteralPath $file)) { throw "Missing presentation: $file" }
        $presentation = $application.Presentations.Open($file, -1, 0, 0)
        try {
            $pdf = Join-Path $outputPath "$name.pdf"
            $renderDirectory = Join-Path $buildPath "$name-render"
            New-Item -ItemType Directory -Force -Path $renderDirectory | Out-Null
            $presentation.SaveAs($pdf, 32)
            $portrait = $name -like '*poster*'
            $width = if ($portrait) { 1260 } else { 1600 }
            $height = if ($portrait) { 1782 } else { 900 }
            foreach ($slide in $presentation.Slides) {
                $slide.Export((Join-Path $renderDirectory ('slide-{0:D2}.png' -f $slide.SlideIndex)), 'PNG', $width, $height)
                foreach ($shape in $slide.Shapes) {
                    if ($shape.HasTextFrame -eq -1 -and $shape.TextFrame.HasText -eq -1) {
                        $range = $shape.TextFrame2.TextRange
                        $usableHeight = $shape.Height - $shape.TextFrame2.MarginTop - $shape.TextFrame2.MarginBottom
                        $checks += [pscustomobject]@{File=$name; Slide=$slide.SlideIndex; Shape=$shape.Name; Text=$shape.TextFrame.TextRange.Text; Height=[math]::Round($shape.Height,2); BoundHeight=[math]::Round($range.BoundHeight,2); Overflow=($range.BoundHeight -gt $usableHeight + 2.0)}
                    }
                }
            }
            Write-Output "Rendered $name : $($presentation.Slides.Count) slides -> $pdf"
        } finally {
            $presentation.Close()
            [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($presentation)
        }
    }
} finally {
    $checks | ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 -LiteralPath (Join-Path $buildPath 'powerpoint-text-fit.json')
    if (!$wasRunning -and $application.Presentations.Count -eq 0) { $application.Quit() }
    [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($application)
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
$bad = @($checks | Where-Object Overflow)
Write-Output "Text shapes checked: $($checks.Count); potential vertical overflow: $($bad.Count)"
$bad | Select-Object File,Slide,Shape,Text,Height,BoundHeight | ConvertTo-Json -Depth 3
