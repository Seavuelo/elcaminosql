@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" tools\setup_godot.py --templates
) else (
    python tools\setup_godot.py --templates
)
if errorlevel 1 pause
