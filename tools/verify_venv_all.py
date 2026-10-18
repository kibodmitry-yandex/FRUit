import os
import sys

sys.path.insert(0, r"F:\FRUit")
# dev-скрипт: данные — в tools\out\testdata, реальный %LOCALAPPDATA% не трогаем
os.environ.setdefault(
    "FRUIT_DATA", os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "testdata")
)
for s in (sys.stdout, sys.stderr):
    try: s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

print("python:", sys.version.split()[0])

# 1) импорт всего пакета
from fruit import core, snapshots, groups, winapi, tabs, icons, cli, tray
import fruit
print("imports OK, version", __import__("fruit").__version__)

import pystray

# --- CLI: save/list/delete без открытия окон ---
print("\n--- CLI save/list/delete ---")
sys.argv = ["fruit"]
cli.main(["save", "_vtest"])
cli.main(["list"])
from fruit import snapshots as sn
wins = snapshots.load_snapshot("_selftest") if False else None
cli.main(["delete", "_utf8test"]) if False else None
cli.main(["delete", "_selftest"])
cli.main(["delete", "_utf8test"])

# --- группы: дедупликация ---
print("\n--- groups dedup ---")
groups.clear()
from fruit import core
wins = core.capture_state()
print("captured:", len(wins))
print("add1:", groups.add_state(wins))
print("add2:", groups.add_state(wins))
ents = groups.load()
print("entries:", len(ents))
sub = sorted(tray._entry_text(e) for e in ents)
for t in sub:
    print("  ", t)

print("\n=== сборка меню ===")
import pystray as ps
from fruit import icons
icon = ps.Icon("fruit", icons.app_icon(64), "FRUit")
items = tray._menu_items(icon)
print("menu items:", len(items))
for it in items:
    try:
        print("   -", repr(it.text))
    except Exception:
        print("   - <separator>")

groups.clear()
print("\nALL OK")
