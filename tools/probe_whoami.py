import os
import sys
import time

with open(r"F:\FRUit\logs\who.log", "a", encoding="utf-8") as f:
    f.write("pid=%s ppid=%s exe=%s launcher=%s argv0=%s\n" % (
        os.getpid(), os.getppid(), sys.executable,
        os.environ.get("__PYVENV_LAUNCHER__"), sys.argv[0]))

time.sleep(6)
