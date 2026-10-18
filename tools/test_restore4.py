import sys, time, os, ctypes
sys.path.insert(0, r"F:\FRUit")
import comtypes
from comtypes import client
comtypes.CoInitialize()
SHDocVw = client.GetModule("shdocvw.dll")
user32 = ctypes.windll.user32

from fruit import core
from fruit.core import Tab, Window

def snap():
    sws = client.CreateObject(SHDocVw.ShellWindows, interface=SHDocVw.IShellWindows)
    d = {}
    for i in range(sws.Count):
        w = sws.Item(i)
        try: u = w.LocationURL
        except Exception: u = ""
        try: h = w.HWND
        except Exception: h = 0
        d.setdefault(h, []).append(u)
    return d

BASE = r"C:\Users\kibod\AppData\Local\Temp\opencode"
paths = [
    BASE + r"\projects\tests",
    BASE + r"\scratch",
    BASE + r"\.tools",
    BASE + r"\projects\dazmanager",
]
for p in paths:
    print("exists %-60s %s" % (p, os.path.isdir(p)))

win = Window(tabs=[Tab(path=p, name=os.path.basename(p)) for p in paths], active=1)

before = set(snap().keys())
print("\nrestoring 1 window / 4 tabs via core.restore_state ...")
summary = core.restore_state([win], group_tabs=True)
print("summary:", summary)

time.sleep(1.5)
after = snap()
newh = [h for h in after if h not in before]
print("new hwnds:", newh)
for h in newh:
    print("  hwnd=%s tabs=%d" % (h, len(after[h])))
    for u in after[h]:
        print("     ", u)

# стабильность
test_hwnd = newh[0] if newh else None
if test_hwnd:
    print("\nstability check:")
    for t in range(1, 7):
        time.sleep(1)
        cur = snap().get(test_hwnd, [])
        print("  t=%ds tabs=%d" % (t, len(cur)))
    print("\nTEST WINDOW hwnd=%s left open for inspection" % test_hwnd)
