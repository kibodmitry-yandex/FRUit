import os, time, ctypes, subprocess
import comtypes
from comtypes import client
comtypes.CoInitialize()
UIA = client.GetModule("UIAutomationCore.dll")
SHDocVw = client.GetModule("shdocvw.dll")
user32 = ctypes.windll.user32
uia = client.CreateObject(UIA.CUIAutomation, interface=UIA.IUIAutomation)

def vlist(a): return [a.GetElement(i) for i in range(a.Length)]
def entries():
    sws = client.CreateObject(SHDocVw.ShellWindows, interface=SHDocVw.IShellWindows)
    out = []
    for i in range(sws.Count):
        w = sws.Item(i)
        try: url = w.LocationURL
        except Exception: url = ""
        try: h = w.HWND
        except Exception: h = 0
        out.append((h, url, w))  # w = IWebBrowser2
    return out
def snap():
    d = {}
    for h,u,_ in entries(): d.setdefault(h,[]).append(u)
    return d
def close_hwnd(h): user32.PostMessageW(h,0x0010,0,0)
def find_button(root,aid):
    c=uia.CreatePropertyCondition(UIA.UIA_ControlTypePropertyId,UIA.UIA_ButtonControlTypeId)
    for b in vlist(root.FindAll(UIA.TreeScope_Descendants,c)):
        if (b.CurrentAutomationId or "")==aid: return b
def invoke(e): e.GetCurrentPattern(UIA.UIA_InvokePatternId).QueryInterface(UIA.IUIAutomationInvokePattern).Invoke()

X=r"C:\Users\kibod\AppData\Local\Temp\opencode\projects\tests"
Y=r"C:\Users\kibod\AppData\Local\Temp\opencode\scratch"

start=set(snap().keys())
subprocess.Popen(["explorer.exe",X]); time.sleep(2.5)
wh=list(set(snap().keys())-start)[0]
root=uia.ElementFromHandle(wh)
print("opened", wh, snap().get(wh))

invoke(find_button(root,"AddButton")); time.sleep(1.2)
print("after add:", snap().get(wh))

# найти запись новой (пустой) вкладки для wh и навигировать её Navigate(Y)
target=None
for h,u,w in entries():
    if h==wh and u=="":
        target=w; break
print("empty-tab entry found:", target is not None)
if target is not None:
    try:
        target.Navigate(Y)
        print("Navigate called OK")
    except Exception as e:
        print("Navigate ERR:", repr(e))
    time.sleep(2.0)
    print("after navigate:", snap().get(wh))

close_hwnd(wh); print("closed", wh)
