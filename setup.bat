@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

echo.
echo ==================================================
echo    SETUP - Media Downloader (YouTube/Twitter/IG)
echo ==================================================
echo.

where winget >nul 2>nul
if not errorlevel 1 goto CHECK_PYTHON
echo [X] winget nao encontrado. Instale pela Microsoft Store, procurando por "App Installer", e rode este arquivo de novo.
pause
exit /b 1

:CHECK_PYTHON
where python >nul 2>nul
if errorlevel 1 goto INSTALL_PYTHON
echo [OK] Python ja esta instalado
goto CHECK_FFMPEG

:INSTALL_PYTHON
echo [ ] Instalando Python...
winget install -e --id Python.Python.3.12
echo [OK] Python instalado. Pode ser necessario reabrir este arquivo depois.

:CHECK_FFMPEG
where ffmpeg >nul 2>nul
if errorlevel 1 goto INSTALL_FFMPEG
echo [OK] ffmpeg ja esta instalado
goto CHECK_DENO

:INSTALL_FFMPEG
echo [ ] Instalando ffmpeg...
winget install -e --id Gyan.FFmpeg
echo [OK] ffmpeg instalado.

:CHECK_DENO
where deno >nul 2>nul
if errorlevel 1 goto INSTALL_DENO
echo [OK] Deno ja esta instalado
goto INSTALL_YTDLP

:INSTALL_DENO
echo [ ] Instalando Deno...
winget install -e --id DenoLand.Deno
echo [OK] Deno instalado.

:INSTALL_YTDLP
echo [ ] Instalando/atualizando yt-dlp...
python -m pip install -U yt-dlp

echo.
echo ==================================================
echo    Setup concluido
echo ==================================================
echo.
echo IMPORTANTE: se algo foi instalado agora pela primeira vez,
echo FECHE esta janela e abra o downloader de novo,
echo para o Windows reconhecer os novos programas.
echo.
echo Para rodar o downloader: python downloader.py
echo.
pause
