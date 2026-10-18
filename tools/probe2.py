import comtypes
from comtypes import client
comtypes.CoInitialize()
SHDocVw = client.GetModule("shdocvw.dll")
sws = SHDocVw.ShellWindows()
print("type:", type(sns) if False else type(sws))
print("dir:", [a for a in dir(sws) if not a.startswith("__")])
