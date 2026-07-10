@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

set "TaskName=ACE_Runtime"
set "ScriptName=start_runtime.vbs"
set "ScriptPath=%~dp0%ScriptName%"
set "StartupFolder=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

echo =============================================
echo ACE Runtime Auto-Start Setup
echo =============================================
echo.
echo Current Path:     %~dp0
echo Script:           %ScriptPath%
echo Startup Folder:   %StartupFolder%
echo.

if not exist "%ScriptPath%" (
    echo [ERROR] Script not found: %ScriptPath%
    pause
    exit /b 1
)

set "ShortcutPath=%StartupFolder%\ACE Runtime.lnk"

if exist "%ShortcutPath%" (
    echo [INFO] Removing existing shortcut...
    del "%ShortcutPath%"
)

echo [INFO] Creating shortcut in Startup folder...

set "VBSFile=%TEMP%\create_shortcut.vbs"
echo Set WshShell = CreateObject("WScript.Shell") > "%VBSFile%"
echo Set shortcut = WshShell.CreateShortcut("%ShortcutPath%") >> "%VBSFile%"
echo shortcut.TargetPath = "%ScriptPath%" >> "%VBSFile%"
echo shortcut.WorkingDirectory = "%~dp0.." >> "%VBSFile%"
echo shortcut.WindowStyle = 7 >> "%VBSFile%"
echo shortcut.Description = "ACE Runtime - Autonomous Civilization Engine" >> "%VBSFile%"
echo shortcut.Save >> "%VBSFile%"

cscript /nologo "%VBSFile%"
del "%VBSFile%"

if exist "%ShortcutPath%" (
    echo.
    echo [OK] Auto-start configured successfully!
    echo.
    echo ACE Runtime will now start AUTOMATICALLY
    echo every time you log into Windows.
    echo.
    echo Logs: %~dp0..\02_MEMORY\logs\runtime_YYYYMMDD.log
    echo.
    echo To manually start now:
    echo   Double-click: %ScriptPath%
    echo.
    echo To stop:
    echo   Run: stop_runtime.ps1
    echo.
    echo To remove auto-start:
    echo   Delete shortcut from:
    echo   %StartupFolder%\ACE Runtime.lnk
    echo.
) else (
    echo [ERROR] Failed to create shortcut
    pause
    exit /b 1
)