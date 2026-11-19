param([int]$StartSlide=1,[int]$EndSlide=40)
$ErrorActionPreference='Stop'
$folder=$PSScriptRoot
$file=Join-Path $folder '.build/v3/candidate.pptx'
$build=Join-Path $folder '.build/v3'
$render=Join-Path $build 'rendered'
New-Item -ItemType Directory -Force -Path $render | Out-Null
$wasRunning=[bool](Get-Process POWERPNT -ErrorAction SilentlyContinue)
$app=New-Object -ComObject PowerPoint.Application
$checks=@()
$tableChecks=@()
try {
 $presentation=$app.Presentations.Open($file,-1,0,0)
 try {
  $presentation.SaveAs((Join-Path $folder '.build/v3/candidate.pdf'),32)
  foreach($slide in $presentation.Slides){
   $footerTop=6.66*72
   foreach($footerShape in $slide.Shapes){
    if($footerShape.HasTextFrame -eq -1 -and $footerShape.TextFrame.HasText -eq -1 -and $footerShape.TextFrame.TextRange.Text -eq 'W&B'){$footerTop=$footerShape.Top}
   }
   if($slide.SlideIndex -ge $StartSlide -and $slide.SlideIndex -le $EndSlide){
    $slide.Export((Join-Path $render ('slide-{0:D2}.png' -f $slide.SlideIndex)),'PNG',1600,900)
   }
   foreach($shape in $slide.Shapes){
    $textShapes=@()
    if($shape.HasTextFrame -eq -1 -and $shape.TextFrame.HasText -eq -1){$textShapes+=,$shape}
    if($shape.HasTable -eq -1){
     $rowSum=0
     foreach($tableRow in $shape.Table.Rows){$rowSum+=$tableRow.Height}
     $actualBottom=[math]::Max($shape.Top+$shape.Height,$shape.Top+$rowSum)
     $tableChecks+=[pscustomobject]@{Slide=$slide.SlideIndex;Table=$shape.Name;BottomInches=[math]::Round($actualBottom/72,4);FooterInches=[math]::Round($footerTop/72,4);GapInches=[math]::Round(($footerTop-$actualBottom)/72,4)}
     for($r=1;$r -le $shape.Table.Rows.Count;$r++){
      for($c=1;$c -le $shape.Table.Columns.Count;$c++){$textShapes+=,$shape.Table.Cell($r,$c).Shape}
     }
    }
    foreach($ts in $textShapes){
     $range=$ts.TextFrame2.TextRange
     $usable=$ts.Height-$ts.TextFrame2.MarginTop-$ts.TextFrame2.MarginBottom
     $checks+=[pscustomobject]@{Slide=$slide.SlideIndex;Text=$ts.TextFrame.TextRange.Text;
      Shape=$ts.Name;Height=[math]::Round($ts.Height,2);BoundHeight=[math]::Round($range.BoundHeight,2);
      Overflow=($range.BoundHeight -gt $usable+2);FontSize=$range.Font.Size}
    }
   }
  }
  Write-Output ('Rendered {0} slides; PDF exported.' -f $presentation.Slides.Count)
 } finally {$presentation.Close();[void][Runtime.InteropServices.Marshal]::ReleaseComObject($presentation)}
} finally {
 $checks | ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 -LiteralPath (Join-Path $build 'text-fit.json')
 $tableChecks | ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 -LiteralPath (Join-Path $build 'native-table-gaps.json')
 if(!$wasRunning -and $app.Presentations.Count -eq 0){$app.Quit()}
 [void][Runtime.InteropServices.Marshal]::ReleaseComObject($app)
 [GC]::Collect();[GC]::WaitForPendingFinalizers()
}
$bad=@($checks|Where-Object Overflow)
Write-Output ('Text/cells checked: {0}; overflow candidates: {1}' -f $checks.Count,$bad.Count)
$bad|Select-Object Slide,Text,Height,BoundHeight|ConvertTo-Json -Depth 3
