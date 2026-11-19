param([switch]$Cuda)
$ErrorActionPreference = 'Stop'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONUTF8 = '1'
if (!(Test-Path -LiteralPath '.venv/Scripts/python.exe')) { python -m venv .venv }
if ($Cuda) {
    .venv/Scripts/python.exe -m pip install torch==2.5.1 torchvision==0.20.1 --index-url https://download.pytorch.org/whl/cu121
    if ($LASTEXITCODE -ne 0) { throw 'CUDA PyTorch installation failed' }
}
.venv/Scripts/python.exe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed' }
if ($Cuda) {
    if (!(Test-Path -LiteralPath '.venv-cpu/Scripts/python.exe')) { python -m venv .venv-cpu }
    .venv-cpu/Scripts/python.exe -m pip install torch==2.5.1 torchvision==0.20.1 --index-url https://download.pytorch.org/whl/cpu
    if ($LASTEXITCODE -ne 0) { throw 'CPU PyTorch installation failed' }
    .venv-cpu/Scripts/python.exe -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw 'CPU dependency installation failed' }
}
.venv/Scripts/python.exe -m scripts.doctor
