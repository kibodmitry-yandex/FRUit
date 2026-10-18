import sys
sys.path.insert(0, r"F:\FRUit")
for stream in (sys.stdout, sys.stderr):
    try: stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

# --- tray smoke test (без запуска message loop) ---
from fruit import tray
import pystray
img = tray._icon_image()
print("icon image:", img.size, img.mode)
icon = pystray.Icon("fruit", img, "FRUit")
icon.menu = tray._build_menu(icon)
print("menu built OK:", type(icon.menu).__name__)

# --- CLI: save + list с русским текстом (проверка UTF-8) ---
from fruit import cli
print("\n--- save ---")
cli.main(["save", "_utf8test"])
print("--- list ---")
cli.main(["list"])
print("--- delete ---")
cli.main(["delete", "_utf8test"])
print("\nALL OK")
