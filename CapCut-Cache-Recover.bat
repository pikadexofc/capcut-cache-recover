@echo off
setlocal EnableDelayedExpansion
title CapCut Cache Recover

:: Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python was not found on your system!
    echo Please install Python 3.9+ from https://www.python.org or the Microsoft Store.
    pause
    exit /b 1
)

:: Ensure project root is in PYTHONPATH
set "SCRIPT_DIR=%~dp0"
if exist "%SCRIPT_DIR%capcut_cache_recover" (
    set "PYTHONPATH=%SCRIPT_DIR%;%PYTHONPATH%"
) else if exist "C:\Users\Shanto\.gemini\antigravity\scratch\capcut-cache-recover\capcut_cache_recover" (
    set "PYTHONPATH=C:\Users\Shanto\.gemini\antigravity\scratch\capcut-cache-recover;%PYTHONPATH%"
)

:: If a file is dragged and dropped onto this script
if "%~1" neq "" (
    echo ========================================================================
    echo   CAPCUT CACHE RECOVER  -  DRAG ^& DROP SALVAGE
    echo ========================================================================
    echo.
    echo [*] Input file: "%~1"
    
    python -m capcut_cache_recover.cli "%~1"
    
    if %ERRORLEVEL% equ 0 (
        echo.
        echo [SUCCESS] Video stream recovered successfully!
        timeout /t 3 >nul
    ) else (
        echo.
        echo [ERROR] Recovery failed. Please check file permissions or format.
        pause
    )
    exit /b 0
)

:: If double-clicked without arguments, launch the modern GUI
echo Starting CapCut Cache Recover GUI...
start "" python -m capcut_cache_recover.gui
exit /b 0
