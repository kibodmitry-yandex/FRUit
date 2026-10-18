import os, time, ctypes, subprocess
from ctypes import wintypes
import comtypes
from comtypes import client
comtypes.CoInitialize()
SHDocVw = client.GetModule("shdocvw.dll")
user32 = ctypes.windll.user32

INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
VkKeyScanW = user32.VkKeyScanW

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort), ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_uint), ("time", ctypes.c_uint),
                ("dwExtraInfo", ctypes.c_size_t)]
class INPUT(ctypes.Structure):
    class _U(ctypes.Union):
        _fields_ = [("ki", KEYBDINPUT)]
    _fields_ = [("type", ctypes.c_uint), ("u", _U)]

def key(vk, flags=0):
    inp = INPUT(type=INPUT_KEYBOARD)
    inp.u.ki = KEYBDINPUT(wVk=vk, wScan=0, dwFlags=flags, time=0, dwExtraInfo=0)
    user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

def type_unicode(s):
    for ch in s:
        inp = INPUT(type=INPUT_KEYBOARD)
        inp.u.ki = KEYBDINPUT(wVk=0, wScan=ord(ch), dwFlags=KEYEVENTF_UNICODE, time=0, dwExtraInfo=0)
        user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))
        inp2 = INPUT(type=INPUT_KEYBOARD)
        inp2.u.ki = KEYBDINPUT(wVk=0, wScan=ord(ch), dwFlags=KEYEVENTF_UNICODE | KEYEVENTF_KEYUP, time=0, dwExtraInfo=0)
        user32.SendInput(1, ctypes.byref(inp2), ctypes.sizeof(inp2))

VK_CONTROL = 0x11
VK_T = 0x54
VK_RETURN = 0x0D

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

X = r"C:\Users\kibod\AppData\Local\Temp\opencode\projects\tests"
Y = r"C:\Users\kibod\AppData\Local\Temp\opencode\scratch"
Z = r"C:\Users\kibod\AppData\Local\Temp\opencode\.tools"

start = set(snap().keys())
print("start hwnds:", start)

# открыть окно с папкой X
subprocess.Popen(["explorer.exe", X])
time.sleep(2.5)
s = snap()
newh = list(set(s.keys()) - start)
print("opened window hwnd:", newh, s.get(newh[0]) if newh else None)
wh = newh[0]

# теперь добавим вкладки Y и Z через Ctrl+T
for folder in (Y, Z):
    user32.SetForegroundWindow(wh)
    time.sleep(0.4)
    key(VK_CONTROL); key(VK_T, KEYEVENTF_KEYUP); key(VK_CONTROL | 0x80, KEYEVENTF_KEYUP)
    # ^ Ctrl down, T down/up, Ctrl up
    time.sleep(0.7)
    type_unicode(folder)
    time.sleep(0.3)
    key(VK_RETURN); key(VK_RETURN, KEYEVENTF_KEYUP)
    time.sleep(1.2)

s2 = snap()
print("after tab automation:")
for h, urls in s2.items():
    print("  hwnd=%-9s n=%d %s" % (h, len(urls), urls))

print("wh still", wh, "-> tabs:", len(s2.get(wh, [])))
close_hwnd(wh)
print("closed test window", wh)
