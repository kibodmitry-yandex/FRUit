import os
import subprocess

py = r"F:\FRUit\.venv\Scripts\pythonw.exe"
probe = r"F:\FRUit\tools\pyw_redirect_probe.py"
log = r"F:\FRUit\logs\probe.log"

forms = {
    "plain /c": 'cmd /c "{py}" "{probe}" >> "{log}" 2>&1',
    "quoted /c": 'cmd /c ""{py}" "{probe}" >> "{log}" 2>&1"',
    "quoted /s /c": 'cmd /s /c ""{py}" "{probe}" >> "{log}" 2>&1"',
}

for name, f in forms.items():
    if os.path.exists(log):
        os.remove(log)
    c = f.format(py=py, probe=probe, log=log)
    subprocess.run(c)          # сырая строка -> как Arguments в C#
    ok = os.path.exists(log)
    body = ""
    if ok:
        with open(log, "r", encoding="utf-8", errors="replace") as fh:
            body = fh.read().strip().replace("\n", " | ")
    print("%-14s -> %s   %s" % (name, "OK" if ok else "NO LOG", body))
