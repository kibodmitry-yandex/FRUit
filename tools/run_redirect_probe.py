import os
import subprocess

log = r"F:\FRUit\logs\probe.log"
if os.path.exists(log):
    os.remove(log)

pyw = r"F:\FRUit\.venv\Scripts\pythonw.exe"
probe = r"C:\Users\kibod\AppData\Local\Temp\opencode\projects\tests\scripts\pyw_redirect_probe.py"
inner = '"%s" "%s" >> "%s" 2>&1' % (pyw, probe, log)
subprocess.run(["cmd", "/c", inner], capture_output=True)

print("--- probe.log ---")
try:
    with open(log, "r", encoding="utf-8", errors="replace") as f:
        print(f.read())
except FileNotFoundError:
    print("(ЛОГ НЕ СОЗДАН!)")
