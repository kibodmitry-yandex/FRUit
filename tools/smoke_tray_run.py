import sys, threading, time
sys.path.insert(0, r"F:\FRUit")
for s in (sys.stdout, sys.stderr):
    try: s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

import pystray
from fruit import tray, icons

icon = pystray.Icon("fruit", icons.app_icon(64), "FRUit — smoke")
icon.menu = pystray.Menu(lambda: tray._menu_items(icon))

err = {}

def run():
    try:
        icon.run()
    except Exception as e:
        err["e"] = repr(e)

t = threading.Thread(target=run, daemon=True)
t.start()
time.sleep(2.5)
print("icon.visible:", icon.visible)
try:
    icon.update_menu()
    print("update_menu OK")
except Exception as e:
    print("update_menu ERR:", e)

# проверим горячие клавиши (pynput) без нажатия — просто регистрацию
try:
    from pynput import keyboard
    hk = keyboard.GlobalHotKeys({tray.HOTKEY_SAVE: lambda: None, tray.HOTKEY_RESTORE: lambda: None})
    hk.start(); time.sleep(0.3); hk.stop()
    print("GlobalHotKeys OK")
except Exception as e:
    print("GlobalHotKeys ERR:", repr(e))

icon.stop()
time.sleep(0.6)
print("run error:", err.get("e"))
print("DONE")
