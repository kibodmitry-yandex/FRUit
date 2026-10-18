import comtypes
from comtypes import client
comtypes.CoInitialize()
SHDocVw = client.GetModule("shdocvw.dll")
sws = client.CreateObject(SHDocVw.ShellWindows, interface=SHDocVw.IShellWindows)
print("count =", sws.Count)
for i in range(sws.Count):
    w = sws.Item(i)
    try: url = w.LocationURL
    except Exception: url = "?"
    try: h = w.HWND
    except Exception: h = "?"
    print("hwnd=%-10s %s" % (h, url))
