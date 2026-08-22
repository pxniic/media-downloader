#Requires -Version 5.1
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$InstallDir = Join-Path $env:LOCALAPPDATA "MediaDownloader"
$ExeName = "MediaDownloader.exe"
$StartMenu = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs"
$ShortcutPath = Join-Path $StartMenu "Media Downloader.lnk"
$RunName = "MediaDownloader"

function Refresh-Path {
    $machine = [Environment]::GetEnvironmentVariable("Path", "Machine")
    $user = [Environment]::GetEnvironmentVariable("Path", "User")
    $env:Path = "$machine;$user"
}

function Ensure-WingetApp($id) {
    $found = winget list --id $id -e 2>$null
    if ($LASTEXITCODE -eq 0 -and $found) {
        Write-Host "[OK] $id"
        return
    }
    Write-Host "[ ] Instalando $id..."
    winget install -e --id $id --accept-package-agreements --accept-source-agreements
    Refresh-Path
}

if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Host "winget nao encontrado. Instale 'App Installer' na Microsoft Store e rode de novo."
    exit 1
}

Write-Host ""
Write-Host "Media Downloader — instalador Windows (.exe, sem Docker)"
Write-Host ""

Ensure-WingetApp "Python.Python.3.12"
Ensure-WingetApp "Gyan.FFmpeg"
Ensure-WingetApp "DenoLand.Deno"
Refresh-Path

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python nao entrou no PATH. Feche o terminal, abra outro e rode o instalador de novo."
    exit 1
}

& (Join-Path $PSScriptRoot "build.ps1")

$DistDir = Join-Path $RepoRoot "dist\MediaDownloader"
if (-not (Test-Path (Join-Path $DistDir $ExeName))) {
    Write-Host "O exe nao foi gerado."
    exit 1
}

New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
Copy-Item (Join-Path $DistDir "*") $InstallDir -Recurse -Force
Copy-Item (Join-Path $PSScriptRoot "uninstall.ps1") (Join-Path $InstallDir "uninstall.ps1") -Force

$ExePath = Join-Path $InstallDir $ExeName

$Wsh = New-Object -ComObject WScript.Shell
$Shortcut = $Wsh.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $ExePath
$Shortcut.WorkingDirectory = $InstallDir
$Shortcut.WindowStyle = 7
$Shortcut.Description = "Media Downloader"
$Shortcut.Save()

$RunKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
New-ItemProperty -Path $RunKey -Name $RunName -Value "`"$ExePath`"" -PropertyType String -Force | Out-Null

Start-Process -FilePath $ExePath -WorkingDirectory $InstallDir

Write-Host ""
Write-Host "Instalado: $ExePath"
Write-Host "Atalho: Menu Iniciar > Media Downloader"
Write-Host "Sobe sozinho no login. Interface: http://127.0.0.1:8765/"
Write-Host "Musicas em: $env:USERPROFILE\Music"
Write-Host ""
Write-Host "Para remover: powershell -ExecutionPolicy Bypass -File `"$InstallDir\uninstall.ps1`""
Write-Host ""
