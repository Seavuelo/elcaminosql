@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" goto dependencies
where py >nul 2>nul
if errorlevel 1 goto python_command
py -3 -m venv .venv
if errorlevel 1 goto error
goto dependencies
:python_command
where python >nul 2>nul
if errorlevel 1 goto missing_python
python -m venv .venv
if errorlevel 1 goto error
:dependencies
".venv\Scripts\python.exe" "%~dp0launch_game.py"
if errorlevel 1 goto error
exit /b 0
:missing_python
echo Necesitas instalar Python 3.10 o superior desde https://www.python.org/downloads/
echo Al instalarlo, activa Add Python to PATH.
:error
echo No se pudo iniciar El Camino SQL. Revisa el mensaje de arriba.
pause
exit /b 1
