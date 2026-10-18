import os, sys, time, ctypes, subprocess
from ctypes import wintypes
import comtypes
from comtypes import client
comtypes.CoInitialize()
SHDocVw = client.GetModule("shdocvw.dll")

def snap():
    sws = client.CreateObject(SHDocVw.ShellWindows, interface=SHDocVw.IShellWindows)
    rows = []
    for i in range(sws.Count):
        w = sws.Item(i)
        try:
            url = w.LocationURL
        except Exception:
            url = ""
        try:
            name = w.LocationName
        except Exception:
            name = ""
        try:
            hwnd = w.HWND
        except Exception:
            hwnd = 0
        rows.append((hwnd, url, name))
    return rows

def dump(tag):
    print("=== %s ===" % tag)
    for hwnd, url, name in snap():
        print("  hwnd=%-10s %-40r %r" % (hwnd, url, name))

dump("BEFORE")

# два тестовых каталога
a = r"C:\Users\kibod\AppData\Local\Temp\opencode\projects\tests"
b = r"C:\Users\kibod\AppData\Local\Temp\opencode\scratch"
# explorer.exe с двумя путями -> одно окно с вкладками или два окна?
subprocess.Popen(["explorer.exe", a, b])
time.sleep(3)
dump("AFTER explorer.exe a b")

# сколько уникальных hwnd (окон) среди file-окон
rows = snap()
hwnds = set(r[0] for r in rows if r[0])
print("unique hwnd count:", len(hwnds), "total entries:", len(rows))
