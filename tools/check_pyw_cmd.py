import subprocess
r = subprocess.run(["wmic", "process", "where", "name='pythonw.exe'",
                    "get", "processid,commandline", "/format:list"],
                   capture_output=True, text=True, encoding="cp866", errors="replace")
for block in r.stdout.split("\n\n"):
    if block.strip():
        print(block.strip())
        print("---")
print("\n=== fruit.log ===")
try:
    with open(r"F:\FRUit\logs\fruit.log", "r", encoding="utf-8", errors="replace") as f:
        print(f.read())
except FileNotFoundError:
    print("(нет лога)")
