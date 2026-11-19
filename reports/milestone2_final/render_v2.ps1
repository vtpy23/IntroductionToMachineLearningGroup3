param([int]$StartSlide=1,[int]$EndSlide=40)
$ErrorActionPreference='Stop'
$folder=$PSScriptRoot
$file=Join-Path $folder 'DSAL_Milestone2_Lab1_Final_v2.pptx'
$build=Join-Path $folder '.build/v2'
$render=Join-Path $build 'rendered'
New-Item -ItemType Directory -Force -Path $render | Out-Null
$wasRunning=[bool](Get-Process POWERPNT -ErrorAction SilentlyContinue)
$app=New-Object -ComObject PowerPoint.Application
$checks=@()
try {
 $presentation=$app.Presentations.Open($file,-1,0,0)
 try {
  $presentation.SaveAs((Join-Path $folder 'DSAL_Milestone2_Lab1_Final_v2.pdf'),32)
  foreach($slide in $presentation.Slides){
   if($slide.SlideIndex -ge $StartSlide -and $slide.SlideIndex -le $EndSlide){
    $slide.Export((Join-Path $render ('slide-{0:D2}.png' -f $slide.SlideIndex)),'PNG',1600,900)
   }
   foreach($shape in $slide.Shapes){
    $textShapes=@()
    if($shape.HasTextFrame -eq -1 -and $shape.TextFrame.HasText -eq -1){$textShapes+=,$shape}
    if($shape.HasTable -eq -1){
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
 if(!$wasRunning -and $app.Presentations.Count -eq 0){$app.Quit()}
 [void][Runtime.InteropServices.Marshal]::ReleaseComObject($app)
 [GC]::Collect();[GC]::WaitForPendingFinalizers()
}
$bad=@($checks|Where-Object Overflow)
Write-Output ('Text/cells checked: {0}; overflow candidates: {1}' -f $checks.Count,$bad.Count)
$bad|Select-Object Slide,Text,Height,BoundHeight|ConvertTo-Json -Depth 3
