import os, time, ctypes, subprocess
from ctypes import wintypes
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
    order = []
    for i in range(sws.Count):
        w = sws.Item(i)
        try: url = w.LocationURL
        except Exception: url = ""
        try: hwnd = w.HWND
        except Exception: hwnd = 0
        d.setdefault(hwnd, []).append(url)
        order.append((hwnd, url))
    return d, order

def close_hwnd(hwnd):
    user32.PostMessageW(hwnd, 0x0010, 0, 0)

X = r"C:\Users\kibod\AppData\Local\Temp\opencode\projects\tests"
Y = r"C:\Users\kibod\AppData\Local\Temp\opencode\scratch"

start = set(snap()[0].keys())
subprocess.Popen(["explorer.exe", X])
time.sleep(2.5)
wh = list(set(snap()[0].keys()) - start)[0]
print("opened window:", wh)

root = uia.ElementFromHandle(wh)

# --- найти кнопку "New tab": печатаем ВСЕ кнопки, ищем name/aid с tab/new/+/вкладк ---
cond = uia.CreatePropertyCondition(UIA.UIA_ControlTypePropertyId, UIA.UIA_ButtonControlTypeId)
btns = vlist(root.FindAll(UIA.TreeScope_Descendants, cond))
print("total buttons:", len(btns))
newtab = None
for b in btns:
    nm = (b.CurrentName or "")
    aid = (b.CurrentAutomationId or "")
    low = (nm + " " + aid).lower()
    if any(k in low for k in ["tab", "new", "+", "вкладк", "нов"]):
        print("  CANDIDATE name=%r aid=%r" % (nm, aid))
        if newtab is None:
            newtab = b
print("newtab chosen:", newtab.CurrentName if newtab else None,
      newtab.CurrentAutomationId if newtab else None)

# --- Invoke новой вкладки ---
if newtab is not None:
    inv = newtab.GetCurrentPattern(UIA.UIA_InvokePatternId)
    inv.Invoke()
    time.sleep(1.2)
    d2, _ = snap()
    print("tabs in window after new-tab invoke:", len(d2.get(wh, [])), d2.get(wh))

    # найти адресную строку (TextBox с Value) и попробоватьSetValue + Enter
    econd = uia.CreatePropertyCondition(UIA.UIA_ControlTypePropertyId, UIA.UIA_EditControlTypeId)
    edits = vlist(root.FindAll(UIA.TreeScope_Descendants, econd))
    addr = None
    for e in edits:
        aid = (e.CurrentAutomationId or "")
        nm = (e.CurrentName or "")
        if aid == "TextBox" or "адрес" in nm.lower() or "address" in nm.lower() or nm.strip().endswith(":"):
            # паттерн Value есть?
            try:
                e.GetCurrentPattern(UIA.UIA_ValuePatternId)
                addr = e
                print("  addr candidate name=%r aid=%r" % (nm, aid))
            except Exception:
                pass
    print("addr chosen:", addr.CurrentName if addr else None)

    if addr is not None:
        vp = addr.GetCurrentPattern(UIA.UIA_ValuePatternId)
        print("  current addr value:", repr(vp.CurrentValue))
        vp.SetValue(Y)
        time.sleep(0.3)
        # отправить Enter в активное окно
        user32.SetForegroundWindow(wh)
        time.sleep(0.3)
        KEYEVENTF_KEYUP = 0x0002
        def tap(vk):
            user32.keybd_event(vk, 0, 0, 0)
            user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
        tap(0x0D)  # VK_RETURN
        time.sleep(1.5)
        d3, _ = snap()
        print("tabs after setvalue+enter:", len(d3.get(wh, [])), d3.get(wh))

close_hwnd(wh)
print("closed", wh)
