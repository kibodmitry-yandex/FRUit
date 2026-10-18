import sys
sys.path.insert(0, r"F:\FRUit")
for s in (sys.stdout, sys.stderr):
    try: s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass
from fruit import core, groups
wins = core.capture_state()
print("captured:", len(wins))
print("added/skipped:", groups.add_state(wins))
print("entries:", len(groups.load()))
