#Requires -Version 5.1
Set-StrictMode -Version Latest
$ErrorActionPreference = "SilentlyContinue"

$InstallDir = Join-Path $env:LOCALAPPDATA "MediaDownloader"
$ShortcutPath = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Media Downloader.lnk"
$RunName = "MediaDownloader"

Get-Process -Name "MediaDownloader" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-CimInstance Win32_Process |
    Where-Object { $_.CommandLine -and $_.CommandLine -like "*MediaDownloader*gui.py*" } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force }

Remove-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -Name $RunName -Force
Remove-Item -Path $ShortcutPath -Force
Remove-Item -Path $InstallDir -Recurse -Force

Write-Host "Media Downloader removido."
Write-Host "Python, ffmpeg e Deno do sistema foram mantidos."
