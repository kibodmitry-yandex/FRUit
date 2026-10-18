import os
import subprocess
import time

log = r"F:\FRUit\logs\fruit.log"
if os.path.exists(log):
    os.remove(log)

subprocess.run([r"F:\FRUit\FRUit.exe"])   # тихий режим: возвращается сразу
time.sleep(3.0)

print("--- fruit.log ---")
try:
    with open(log, "r", encoding="utf-8", errors="replace") as f:
        print(f.read())
except FileNotFoundError:
    print("(ЛОГ НЕ СОЗДАН!)")
