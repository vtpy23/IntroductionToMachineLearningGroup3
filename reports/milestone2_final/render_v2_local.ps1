param([string]$InputPptx='')
$ErrorActionPreference='Stop'
$folder=$PSScriptRoot
$root=Split-Path (Split-Path $folder -Parent) -Parent
$build=Join-Path $folder '.build/v2'
$images=Join-Path $build 'rendered'
New-Item -ItemType Directory -Force -Path $images | Out-Null
if(!$InputPptx){$InputPptx=Join-Path $build 'candidate.pptx'}
$lo=Join-Path $root 'artifacts/render-tools/portable/App/libreoffice/program/soffice.com'
if(!(Test-Path -LiteralPath $lo)){throw 'Portable renderer missing. See FINAL_CHECKLIST.md; no experiment environment changes are needed.'}
$profileUri=([System.Uri](Join-Path $root 'artifacts/render-tools/lo-profile')).AbsoluteUri
& $lo ('-env:UserInstallation='+$profileUri) --headless --nologo --nofirststartwizard --nodefault --convert-to pdf:impress_pdf_Export --outdir $build $InputPptx
if($LASTEXITCODE -ne 0){throw 'PDF conversion failed'}
$pdf=Join-Path $build (([IO.Path]::GetFileNameWithoutExtension($InputPptx))+'.pdf')
$pdfArg=Resolve-Path -LiteralPath $pdf -Relative
$imageArg=Join-Path (Resolve-Path -LiteralPath $images -Relative) 'slide'
& pdftoppm -png -scale-to 1600 $pdfArg $imageArg
if($LASTEXITCODE -ne 0){throw 'PDF rasterization failed'}
Write-Output ('PDF: '+$pdf)
