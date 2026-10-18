import os, time, ctypes, subprocess
import comtypes
from comtypes import client
comtypes.CoInitialize()
UIA = client.GetModule("UIAutomationCore.dll")
SHDocVw = client.GetModule("shdocvw.dll")
user32 = ctypes.windll.user32
uia = client.CreateObject(UIA.CUIAutomation, interface=UIA.IUIAutomation)
INPUT_KEYBOARD=1; KEYEVENTF_KEYUP=0x0002

class KEYBDINPUT(ctypes.Structure):
    _fields_=[("wVk",ctypes.c_ushort),("wScan",ctypes.c_ushort),("dwFlags",ctypes.c_uint),("time",ctypes.c_uint),("dwExtraInfo",ctypes.c_size_t)]
class INPUT(ctypes.Structure):
    class _U(ctypes.Union): _fields_=[("ki",KEYBDINPUT)]
    _fields_=[("type",ctypes.c_uint),("u",_U)]
def send_vk(vk,up=False):
    inp=INPUT(type=INPUT_KEYBOARD); inp.u.ki=KEYBDINPUT(wVk=vk,dwFlags=(KEYEVENTF_KEYUP if up else 0))
    user32.SendInput(1,ctypes.byref(inp),ctypes.sizeof(INPUT))

def vlist(a): return [a.GetElement(i) for i in range(a.Length)]
def snap():
    sws=client.CreateObject(SHDocVw.ShellWindows,interface=SHDocVw.IShellWindows); d={}
    for i in range(sws.Count):
        w=sws.Item(i)
        try:u=w.LocationURL
        except Exception:u=""
        try:h=w.HWND
        except Exception:h=0
        d.setdefault(h,[]).append(u)
    return d
def close_hwnd(h): user32.PostMessageW(h,0x0010,0,0)
def find_button(root,aid):
    c=uia.CreatePropertyCondition(UIA.UIA_ControlTypePropertyId,UIA.UIA_ButtonControlTypeId)
    for b in vlist(root.FindAll(UIA.TreeScope_Descendants,c)):
        if (b.CurrentAutomationId or "")==aid: return b
def invoke(e): e.GetCurrentPattern(UIA.UIA_InvokePatternId).QueryInterface(UIA.IUIAutomationInvokePattern).Invoke()

def addr_bar(root):
    """Первый TextBox с aid=TextBox (адресная строка), не поиск."""
    ec=uia.CreatePropertyCondition(UIA.UIA_ControlTypePropertyId,UIA.UIA_EditControlTypeId)
    for e in vlist(root.FindAll(UIA.TreeScope_Descendants,ec)):
        if (e.CurrentAutomationId or "")=="TextBox":
            return e
    return None

X=r"C:\Users\kibod\AppData\Local\Temp\opencode\projects\tests"
Y=r"C:\Users\kibod\AppData\Local\Temp\opencode\scratch"

start=set(snap().keys())
subprocess.Popen(["explorer.exe",X]); time.sleep(2.5)
wh=list(set(snap().keys())-start)[0]
root=uia.ElementFromHandle(wh)
invoke(find_button(root,"AddButton")); time.sleep(1.0)
print("after add:", snap().get(wh))

ab=addr_bar(root)
print("addr bar:", ab.CurrentName if ab else None)
ab.SetFocus(); time.sleep(0.4)
vp=ab.GetCurrentPattern(UIA.UIA_ValuePatternId).QueryInterface(UIA.IUIAutomationValuePattern)
print("addr editable value before:", repr(vp.CurrentValue))
vp.SetValue(Y); time.sleep(0.3)
print("addr value after set:", repr(vp.CurrentValue))
send_vk(0x0D); send_vk(0x0D,up=True)   # Enter
time.sleep(2.0)
print("after setnav:", snap().get(wh))
close_hwnd(wh); print("closed", wh)
