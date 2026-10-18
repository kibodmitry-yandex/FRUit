@echo off
rem Build the thin FRUit exe launcher (it only runs the current python -m fruit).
rem No dependencies: C# compiler shipped with Windows (.NET Framework).
setlocal
set "CSC=C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
if not exist "%CSC%" set "CSC=C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe"
if not exist "%CSC%" (
  echo [build] csc.exe not found - need .NET Framework 4.x
  exit /b 2
)
set "HERE=%~dp0"

rem Иконка генерируется кодом (Pillow). Если её нет — сделаем venv-питоном.
if not exist "%HERE%fruit.ico" (
  if exist "%HERE%..\.venv\Scripts\python.exe" (
    echo [build] generating icon...
    "%HERE%..\.venv\Scripts\python.exe" "%HERE%make_icon.py"
  ) else (
    echo [build] warning: fruit.ico missing and .venv python not found
  )
)

set "OUT=%HERE%..\FRUit.exe"
echo [build] %CSC%
echo [build] -^> %OUT%
"%CSC%" /nologo /target:winexe /optimize+ /win32icon:"%HERE%fruit.ico" /out:"%OUT%" "%HERE%FruitLauncher.cs"
echo [build] rc=%errorlevel%
endlocal
