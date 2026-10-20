@echo off
rem ============================================================
rem  FRUit - one-click setup (safe to run twice: .venv is reused)
rem
rem  1. finds Python 3.9+ ("py -3" or "python");
rem  2. if there is none - installs it silently via winget
rem     (set FRUIT_INSTALL_NOAUTO=1 to disable auto-install);
rem  3. creates .venv in this folder and installs requirements.txt.
rem
rem  FRUit.exe uses .venv\Scripts\pythonw.exe, so after this script
rem  the tray launcher just works.
rem ============================================================
setlocal EnableExtensions
cd /d "%~dp0"

echo ============================================
echo  FRUit setup
echo ============================================
echo.

call :find_python
if defined PYCMD goto :step_venv

echo [1/3] Python 3.9+ not found.
if defined FRUIT_INSTALL_NOAUTO goto :manual
where winget >nul 2>nul
if errorlevel 1 goto :manual

echo        Installing Python via winget (may take a minute)...
winget install --id Python.Python.3.12 --scope user --silent --accept-package-agreements --accept-source-agreements >nul
if errorlevel 1 winget install --id Python.Python.3 --scope user --silent --accept-package-agreements --accept-source-agreements >nul
call :refresh_path
call :find_python
if not defined PYCMD for /d %%D in ("%LocalAppData%\Programs\Python\Python*") do if exist "%%D\python.exe" set "PYCMD=""%%D\python.exe"""
if defined PYCMD goto :step_venv

echo        Python is still not visible in this window.
echo        Close it, run install.bat again - the new window will see it.
goto :fail

:manual
echo        Install Python 3.9+ manually from https://www.python.org/downloads/
echo        and tick "Add python.exe to PATH", then run install.bat again.
goto :fail

:step_venv
echo [1/3] Python: %PYCMD%

echo [2/3] Virtual environment (.venv)...
if exist ".venv\Scripts\python.exe" (
    echo        existing .venv found, reusing it
) else (
    %PYCMD% -m venv .venv
    if errorlevel 1 goto :fail_venv
)
if not exist ".venv\Scripts\python.exe" goto :fail_venv

echo [3/3] Dependencies: comtypes, pystray, Pillow, pynput...
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -q -r requirements.txt
if errorlevel 1 goto :fail_pip
".venv\Scripts\python.exe" -c "import comtypes, pystray, PIL, pynput" >nul 2>nul
if errorlevel 1 goto :fail_pip

echo.
echo  Done. Start FRUit now?
choice /c YN /n /m "  [Y] yes / [N] no: "
if errorlevel 2 goto :bye
if exist "%~dp0FRUit.exe" (
    start "" "%~dp0FRUit.exe"
) else (
    start "" "%~dp0.venv\Scripts\pythonw.exe" -X utf8 -m fruit tray
)
:bye
echo.
echo  FRUit is in the tray (folder icon with a banana), right-click for the menu.
echo  Logs: logs\fruit.log
pause
exit /b 0

:fail_venv
echo.
echo  ERROR: could not create .venv - check the messages above.
goto :fail

:fail_pip
echo.
echo  ERROR: could not install dependencies - check the messages above.
echo  It may be no internet access; run install.bat again when it is back.
goto :fail

:fail
echo.
pause
exit /b 1

:: ------------------------------------------------------------
:: set PYCMD to a launcher that has Python >= 3.9
:: (the Microsoft Store "python.exe" stub fails the check - good)
:: ------------------------------------------------------------
:find_python
set "PYCMD="
where py >nul 2>nul
if errorlevel 1 goto :find_plain
py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 9) else 1)" >nul 2>nul
if errorlevel 1 goto :find_plain
set "PYCMD=py -3"
exit /b 0
:find_plain
where python >nul 2>nul
if errorlevel 1 exit /b 1
python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 9) else 1)" >nul 2>nul
if errorlevel 1 exit /b 1
set "PYCMD=python"
exit /b 0

:: ------------------------------------------------------------
:: re-read PATH from the registry: after a winget install the
:: current window still has the old PATH
:: ------------------------------------------------------------
:refresh_path
set "PATH_USER="
set "PATH_MACH="
for /f "usebackq tokens=1,2*" %%A in (`reg query "HKCU\Environment" /v Path 2^>nul`) do if /i "%%A"=="Path" set "PATH_USER=%%B"
for /f "usebackq tokens=1,2*" %%A in (`reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul`) do if /i "%%A"=="Path" set "PATH_MACH=%%B"
set "PATH=%PATH_USER%;%PATH_MACH%;%SystemRoot%\System32;%SystemRoot%;%SystemRoot%\System32\Wbem"
exit /b 0
