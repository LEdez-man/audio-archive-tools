@echo off
chcp 65001 >nul
rem Drag a folder with recordings onto this file to set it up as an audio archive.
rem Einen Ordner mit Aufnahmen auf diese Datei ziehen, um ihn als Audioarchiv einzurichten.
if "%~1"=="" (
  echo Drag a folder with recordings onto this file. / Bitte einen Ordner auf diese Datei ziehen.
  pause
  exit /b
)
set "PYTHONIOENCODING=utf-8"
python "%~dp0audio_archive\setup_archive.py" %*
echo.
pause
