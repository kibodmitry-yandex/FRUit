import os
import sys

sys.path.insert(0, r"F:\FRUit")
# dev-скрипт: данные — в tools\out\testdata, реальный %LOCALAPPDATA% не трогаем
os.environ.setdefault(
    "FRUIT_DATA", os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "testdata")
)

# импорт всех модулей — ловим ошибки синтаксиса/зависимостей
from fruit import core, snapshots, winapi, tabs, cli
print("core/snapshots/winapi/tabs/cli import OK")
try:
    from fruit import tray
    print("tray import OK")
except Exception as e:
    print("tray import ERR:", repr(e))

print("\n--- save ---")
print("rc =", cli.main(["save", "_selftest"]))

print("\n--- list ---")
cli.main(["list"])

print("\n--- load round-trip ---")
wins = snapshots.load_snapshot("_selftest")
print("windows:", len(wins))
for w in wins:
    print("  tabs=%d active=%d geo=%s" % (len(w.tabs), w.active, w.geometry))
    for t in w.tabs:
        print("     path=%r name=%r virtual=%s" % (t.path, t.name, t.virtual))

print("\n--- delete ---")
print("rc =", cli.main(["delete", "_selftest"]))
