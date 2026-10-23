@echo off
chcp 65001 >nul
cd /d "%~dp0"
if exist "%~dp0Cornell_Korean_Editor.exe" (
 start "" "%~dp0Cornell_Korean_Editor.exe"
 exit /b
)
python -X utf8 "%~dp0tools\launch_editor.py"
if errorlevel 1 pause
