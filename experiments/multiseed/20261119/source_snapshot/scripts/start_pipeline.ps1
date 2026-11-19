param([ValidateSet('offline','online','disabled')][string]$Tracking = 'offline', [ValidateSet('auto','cpu','cuda')][string]$Compute = 'auto')
$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$projectPath = Split-Path -Parent $PSScriptRoot
$pythonPath = Join-Path $projectPath '.venv/Scripts/python.exe'
$logDirectory = Join-Path $projectPath 'outputs/pipeline'
New-Item -ItemType Directory -Force -Path $logDirectory | Out-Null
$pidFile = Join-Path $logDirectory 'process.json'
if (Test-Path -LiteralPath $pidFile) {
    $existing = Get-Content -Raw -LiteralPath $pidFile | ConvertFrom-Json
    $existingProcess = Get-Process -Id $existing.pid -ErrorAction SilentlyContinue
    if ($existingProcess -and ($existingProcess.StartTime.ToUniversalTime().ToString('o') -eq $existing.startedUtc)) {
        throw "Pipeline is already running (PID $($existing.pid))"
    }
}
if (Test-Path -LiteralPath (Join-Path $projectPath '.stop-project')) {
    throw 'Pause flag .stop-project exists. Remove that file to resume.'
}
$process = Start-Process -FilePath $pythonPath -ArgumentList @('-X','utf8','-m','scripts.pipeline','--tracking',$Tracking,'--compute',$Compute) -WorkingDirectory $projectPath -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logDirectory 'launcher.stdout.log') -RedirectStandardError (Join-Path $logDirectory 'launcher.stderr.log') -PassThru
@{pid=$process.Id; startedUtc=$process.StartTime.ToUniversalTime().ToString('o'); tracking=$Tracking} | ConvertTo-Json | Set-Content -Encoding UTF8 -LiteralPath $pidFile
Write-Output "Pipeline started (PID $($process.Id)). Logs: outputs/pipeline. Create .stop-project to pause after the current epoch or run."
