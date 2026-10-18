import comtypes
from comtypes import client
comtypes.CoInitialize()
SHDocVw = client.GetModule("shdocvw.dll")

print("IShellWindows exists:", hasattr(SHDocVw, "IShellWindows"))
sws = client.CreateObject(SHDocVw.ShellWindows, interface=SHDocVw.IShellWindows)
print("type:", type(sws))
print("dir:", [a for a in dir(sws) if not a.startswith("_")])
print("Count:", sws.Count)
