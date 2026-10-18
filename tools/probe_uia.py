import os, time, ctypes, subprocess
import comtypes
from comtypes import client
comtypes.CoInitialize()
UIA = client.GetModule("UIAutomationCore.dll")
user32 = ctypes.windll.user32

# правильная инстанциация IUIAutomation
uia = client.CreateObject(UIA.CUIAutomation, interface=UIA.IUIAutomation)
print("uia type:", type(uia))
print("has ElementFromHandle:", hasattr(uia, "ElementFromHandle"))

def vlist(arr):
    out = []
    for i in range(arr.Length):
        out.append(arr.GetElement(i))
    return out

def snap_hwnds():
    SHDocVw = client.GetModule("shdocvw.dll")
    sws = client.CreateObject(SHDocVw.ShellWindows, interface=SHDocVw.IShellWindows)
    d = {}
    for i in range(sws.Count):
        w = sws.Item(i)
        try: url = w.LocationURL
        except Exception: url = ""
        try: hwnd = w.HWND
        except Exception: hwnd = 0
        d.setdefault(hwnd, []).append(url)
    return d

def close_hwnd(hwnd):
    user32.PostMessageW(hwnd, 0x0010, 0, 0)

X = r"C:\Users\kibod\AppData\Local\Temp\opencode\projects\tests"
start = set(snap_hwnds().keys())
subprocess.Popen(["explorer.exe", X])
time.sleep(2.5)
newh = list(set(snap_hwnds().keys()) - start)
wh = newh[0]
print("test window hwnd:", wh)

root = uia.ElementFromHandle(wh)
print("root name:", root.CurrentName, "cls:", root.CurrentClassName)

CT = UIA.UIA_ControlTypePropertyId
# переберем интересные control types в окне
for label, ctid in [("Button", UIA.UIA_ButtonControlTypeId),
                    ("Tab", UIA.UIA_TabControlTypeId),
                    ("TabItem", UIA.UIA_TabItemControlTypeId),
                    ("Edit", UIA.UIA_EditControlTypeId),
                    ("ComboBox", UIA.UIA_ComboBoxControlTypeId)]:
    cond = uia.CreatePropertyCondition(CT, ctid)
    arr = root.FindAll(UIA.TreeScope_Descendants, cond)
    els = vlist(arr)
    print("-- %s: %d" % (label, len(els)))
    for e in els[:12]:
        nm = e.CurrentName
        aid = e.CurrentAutomationId
        cls = e.CurrentClassName
        # какие паттерны доступны
        pats = []
        for pname, pid in [("Invoke", UIA.UIA_InvokePatternId),
                           ("Value", UIA.UIA_ValuePatternId),
                           ("SelectionItem", UIA.UIA_SelectionItemPatternId),
                           ("LegacyIAccessible", UIA.UIA_LegacyIAccessiblePatternId)]:
            try:
                p = e.GetCurrentPattern(pid)
                if p: pats.append(pname)
            except Exception:
                pass
        print("    name=%r cls=%r aid=%r pats=%s" % (nm, cls, aid, pats))

close_hwnd(wh)
print("closed", wh)
