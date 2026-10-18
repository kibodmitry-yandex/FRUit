import os, time, ctypes, subprocess
import comtypes
from comtypes import client
comtypes.CoInitialize()
UIA = client.GetModule("UIAutomationCore.dll")
SHDocVw = client.GetModule("shdocvw.dll")
user32 = ctypes.windll.user32

uia = client.CreateObject(UIA.CUIAutomation, interface=UIA.IUIAutomation)

def vlist(arr):
    return [arr.GetElement(i) for i in range(arr.Length)]

def snap():
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

def find_button(root, aid):
    cond = uia.CreatePropertyCondition(UIA.UIA_ControlTypePropertyId, UIA.UIA_ButtonControlTypeId)
    for b in vlist(root.FindAll(UIA.TreeScope_Descendants, cond)):
        if (b.CurrentAutomationId or "") == aid:
            return b
    return None

def invoke(elem):
    p = elem.GetCurrentPattern(UIA.UIA_InvokePatternId)
    inv = p.QueryInterface(UIA.IUIAutomationInvokePattern)
    inv.Invoke()

X = r"C:\Users\kibod\AppData\Local\Temp\opencode\projects\tests"
Y = r"C:\Users\kibod\AppData\Local\Temp\opencode\scratch"

start = set(snap().keys())
subprocess.Popen(["explorer.exe", X])
time.sleep(2.5)
wh = list(set(snap().keys()) - start)[0]
print("opened window:", wh)
root = uia.ElementFromHandle(wh)

btn = find_button(root, "AddButton")
print("AddButton found:", bool(btn))
if btn:
    invoke(btn)
    time.sleep(1.2)
    print("tabs after add:", len(snap().get(wh, [])), snap().get(wh))

    # адресная строка = фокус после клика по Add New Tab
    fe = uia.GetFocusedElement()
    print("focused:", fe.CurrentName, "| cls:", fe.CurrentClassName, "| aid:", fe.CurrentAutomationId,
          "| ctltype:", fe.CurrentControlType)
    # привести к ValuePattern
    try:
        p = fe.GetCurrentPattern(UIA.UIA_ValuePatternId)
        vp = p.QueryInterface(UIA.IUIAutomationValuePattern)
        print("focused is Value-capable, cur:", repr(vp.CurrentValue))
        vp.SetValue(Y)
        time.sleep(0.3)
        user32.SetForegroundWindow(wh)
        time.sleep(0.2)
        user32.keybd_event(0x0D, 0, 0, 0)
        user32.keybd_event(0x0D, 0, 0x0002, 0)
        time.sleep(1.5)
        print("tabs after setvalue+enter:", len(snap().get(wh, [])), snap().get(wh))
    except Exception as e:
        print("focused not value/commit failed:", repr(e))

close_hwnd(wh)
print("closed", wh)
