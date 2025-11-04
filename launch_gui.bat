@echo off
REM Webcam Settings GUI Launcher
REM Automatically detects and launches webcam settings dialog

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.7 or later from https://www.python.org/
    pause
    exit /b 1
)

REM Launch the GUI
python "%~dp0webcam_settings_gui.py"

REM Check if the GUI launched successfully
if errorlevel 1 (
    echo.
    echo Failed to launch the GUI application.
    echo Please ensure Python is properly installed with tkinter support.
    pause
    exit /b 1
)
