import subprocess
r = subprocess.run(["tasklist", "/FI", "IMAGENAME eq pythonw.exe"],
                   capture_output=True, text=True, encoding="cp866", errors="replace")
print(r.stdout)
