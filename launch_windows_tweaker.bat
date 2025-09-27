@echo off
REM Windows Tweaker Launcher
REM Activates venv and runs the app as a module

SETLOCAL

REM Set venv path (edit if your venv is elsewhere)
SET VENV_DIR=.venv

REM Activate venv
CALL %VENV_DIR%\Scripts\activate.bat

REM Run the app
python -m windows11_tweaker.main

ENDLOCAL
