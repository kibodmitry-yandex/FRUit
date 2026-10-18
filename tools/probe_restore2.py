import os, time, ctypes, subprocess
from ctypes import wintypes
import comtypes
from comtypes import client
comtypes.CoInitialize()
SHDocVw = client.GetModule("shdocvw.dll")
user32 = ctypes.windll.user32

def snap():
    sws = client.CreateObject(SHDocVw.ShellWindows, interface=SHDocVw.IShellWindows)
    d = {}
    for i in range(sws.Count):
        w = sws.Item(i)
        try:
            url = w.LocationURL
        except Exception:
            url = ""
        try:
            hwnd = w.HWND
        except Exception:
            hwnd = 0
        d.setdefault(hwnd, []).append(url)
    return d

def close_hwnd(hwnd):
    user32.PostMessageW(hwnd, 0x0010, 0, 0)  # WM_CLOSE

# --- cleanup: закрыть окно "Документы", которое я открыл в прошлом тесте ---
before = snap()
print("BEFORE cleanup hwnds:", {h: v for h, v in before.items()})
for h, urls in list(before.items()):
    joined = " ".join(urls)
    if "OneDrive" in joined and ("%D0%94" in joined or "Документ" in joined):
        print("  closing test window hwnd", h, urls)
        close_hwnd(h)
time.sleep(1.5)
print("AFTER cleanup:", list(snap().keys()))

# --- тест: открыть папку X, потом папку Y. Одно окно (вкладки) или два? ---
X = r"C:\Users\kibod\AppData\Local\Temp\opencode\projects\tests"
Y = r"C:\Users\kibod\AppData\Local\Temp\opencode\scratch"

start_hwnds = set(snap().keys())
print("start hwnds:", start_hwnds)

subprocess.Popen(["explorer.exe", X])
time.sleep(2.5)
s1 = snap()
new1 = set(s1.keys()) - start_hwnds
print("after X -> new hwnds:", new1, "urls:", {h: s1[h] for h in new1})

subprocess.Popen(["explorer.exe", Y])
time.sleep(2.5)
s2 = snap()
new2 = set(s2.keys()) - start_hwnds
print("after Y -> new hwnds:", new2, "urls:", {h: s2[h] for h in new2})

if new1 & new2:
    print("RESULT: Y joined X's window -> TABS work via separate launches")
else:
    print("RESULT: separate windows -> each folder = own window")

# --- cleanup: закрыть только что открытые тестовые окна ---
for h in (new1 | new2):
    print("  closing test hwnd", h)
    close_hwnd(h)
time.sleep(1)
print("final hwnds:", list(snap().keys()))
