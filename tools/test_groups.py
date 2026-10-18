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

from fruit import core, groups, tray, icons
import pystray

print("=== очистка хранилища ===")
groups.clear()
print("store:", groups.store_path())
print("entries after clear:", len(groups.load()))

print("\n=== съём текущих окон ===")
wins = core.capture_state()
print("captured windows:", len(wins))

print("\n=== 1-е добавление (все новые) ===")
a1, s1 = groups.add_state(wins)
print("added=%d skipped=%d" % (a1, s1))

print("\n=== 2-е добавление (полные дубли -> пропуск) ===")
a2, s2 = groups.add_state(wins)
print("added=%d skipped=%d" % (a2, s2))

entries = groups.load()
print("\n=== записи в хранилище ===")
for e in entries:
    print("  kind=%-6s label=%-22s tabs=%d" % (e["kind"], e["label"], len(e["tabs"])))

print("\n=== entry_window(первая запись) ===")
w = groups.entry_window(entries[0]["id"])
print("  окно: tabs=%d active=%d geo=%s" % (len(w.tabs), w.active,
      None if not w.geometry else (w.geometry.left, w.geometry.top, w.geometry.width, w.geometry.height, w.geometry.state)))

print("\n=== сборка меню трея ===")
icon = pystray.Icon("fruit", icons.app_icon(64), "FRUit")
items = tray._menu_items(icon)
print("  пунктов меню:", len(items))
for it in items:
    try:
        print("   -", repr(it.text))
    except Exception:
        print("   - <separator>")

print("\n=== удаление первой записи ===")
ok = groups.remove(entries[0]["id"])
print("  remove:", ok, "-> entries:", len(groups.load()))

print("\n=== иконка ===")
im = icons.app_icon(64)
print("  app_icon:", im.size, im.mode)

print("\n--- очистка после теста ---")
groups.clear()
print("entries:", len(groups.load()))
print("\nALL OK")
