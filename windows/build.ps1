#Requires -Version 5.1
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python nao encontrado. Rode windows\\install.ps1 ou instale Python 3.12."
    exit 1
}

Write-Host "[ ] Preparando PyInstaller..."
python -m pip install -q -U pip pyinstaller
python -m pip install -q -r (Join-Path $RepoRoot "requirements.txt")

Write-Host "[ ] Gerando MediaDownloader.exe..."
python -m PyInstaller --noconfirm --clean (Join-Path $RepoRoot "MediaDownloader.spec")

$Exe = Join-Path $RepoRoot "dist\MediaDownloader\MediaDownloader.exe"
if (-not (Test-Path $Exe)) {
    Write-Host "Falha ao gerar o exe."
    exit 1
}

Write-Host "[OK] $Exe"
