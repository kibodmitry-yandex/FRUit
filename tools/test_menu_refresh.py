"""Проверка: после снапшота обновляются и меню, и подсказка (title) значка.

Пишет в отдельный каталог данных (FRUIT_DATA -> tools/out/testdata), чтобы не
затирать реальный %LOCALAPPDATA%\\FRUit.
"""

import os
import sys
import threading
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ["FRUIT_DATA"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "out", "testdata"
)
for s in (sys.stdout, sys.stderr):
    try:
        s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import pystray  # noqa: E402

from fruit import groups, icons, tray  # noqa: E402

groups.clear()

icon = pystray.Icon("fruit", icons.app_icon(64), "FRUit test")
icon.menu = tray._make_menu(icon)
tray._ICON = icon

err = {}


def run():
    try:
        icon.run()
    except Exception as e:  # noqa: BLE001
        err["e"] = repr(e)


threading.Thread(target=run, daemon=True).start()
time.sleep(1.5)

print("до снапшота : entries=%d  title=%r" % (len(groups.load()), icon.title))

tray.make_snapshot()
time.sleep(0.6)

print("после снапшота: entries=%d  title=%r" % (len(groups.load()), icon.title))
print("пункты меню:")
for it in tray._menu_items(icon):
    try:
        print("   -", it.text)
    except Exception:
        print("   - <separator>")

icon.stop()
time.sleep(0.4)
print("run error:", err.get("e"))
groups.clear()
print("DONE")
