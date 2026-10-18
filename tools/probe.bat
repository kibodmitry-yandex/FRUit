@echo off
rem Проверка: пишет ли pythonw в перенаправленный файл (как это делает лаунчер).
del /q "F:\FRUit\logs\probe.log" 2>nul
"F:\FRUit\.venv\Scripts\pythonw.exe" "C:\Users\kibod\AppData\Local\Temp\opencode\projects\tests\scripts\pyw_redirect_probe.py" >> "F:\FRUit\logs\probe.log" 2>&1
echo bat-exit=%errorlevel%
