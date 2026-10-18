import os, time, ctypes, subprocess
import comtypes
from comtypes import client
comtypes.CoInitialize()
UIA = client.GetModule("UIAutomationCore.dll")
SHDocVw = client.GetModule("shdocvw.dll")
user32 = ctypes.windll.user32

uia = client.CreateObject(UIA.CUIAutomation, interface=UIA.IUIAutomation)
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort), ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_uint), ("time", ctypes.c_uint),
                ("dwExtraInfo", ctypes.c_size_t)]
class INPUT(ctypes.Structure):
    class _U(ctypes.Union):
        _fields_ = [("ki", KEYBDINPUT)]
    _fields_ = [("type", ctypes.c_uint), ("u", _U)]

def send_vk(vk, up=False):
    inp = INPUT(type=INPUT_KEYBOARD)
    inp.u.ki = KEYBDINPUT(wVk=vk, dwFlags=(KEYEVENTF_KEYUP if up else 0))
    user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))

def type_unicode(s):
    for ch in s:
        for up in (False, True):
            inp = INPUT(type=INPUT_KEYBOARD)
            inp.u.ki = KEYBDINPUT(wVk=0, wScan=ord(ch),
                                  dwFlags=KEYEVENTF_UNICODE | (KEYEVENTF_KEYUP if up else 0))
            user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))

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
    p.QueryInterface(UIA.IUIAutomationInvokePattern).Invoke()

X = r"C:\Users\kibod\AppData\Local\Temp\opencode\projects\tests"
Y = r"C:\Users\kibod\AppData\Local\Temp\opencode\scratch"

start = set(snap().keys())
subprocess.Popen(["explorer.exe", X])
time.sleep(2.5)
wh = list(set(snap().keys()) - start)[0]
root = uia.ElementFromHandle(wh)
print("opened:", wh, "tabs:", snap().get(wh))

btn = find_button(root, "AddButton")
invoke(btn)
time.sleep(1.0)
print("after AddButton tabs:", snap().get(wh))

# навигация: Ctrl+L, ввод пути, Enter
user32.SetForegroundWindow(wh)
time.sleep(0.3)
send_vk(0x11)                 # Ctrl down
send_vk(0x4C)                 # L down
send_vk(0x4C, up=True)        # L up
send_vk(0x11, up=True)        # Ctrl up
time.sleep(0.4)
type_unicode(Y)
time.sleep(0.3)
send_vk(0x0D)                 # Enter
send_vk(0x0D, up=True)
time.sleep(1.8)
print("after nav tabs:", snap().get(wh))

close_hwnd(wh)
print("closed", wh)
