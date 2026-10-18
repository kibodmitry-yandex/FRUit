import os, time, ctypes, subprocess
import comtypes
from comtypes import client
comtypes.CoInitialize()
UIA = client.GetModule("UIAutomationCore.dll")
SHDocVw = client.GetModule("shdocvw.dll")
user32 = ctypes.windll.user32

uia = client.CreateObject(UIA.CUIAutomation, interface=UIA.IUIAutomation)
INPUT_KEYBOARD=1; KEYEVENTF_KEYUP=0x0002; KEYEVENTF_UNICODE=0x0004

class KEYBDINPUT(ctypes.Structure):
    _fields_=[("wVk",ctypes.c_ushort),("wScan",ctypes.c_ushort),("dwFlags",ctypes.c_uint),("time",ctypes.c_uint),("dwExtraInfo",ctypes.c_size_t)]
class INPUT(ctypes.Structure):
    class _U(ctypes.Union): _fields_=[("ki",KEYBDINPUT)]
    _fields_=[("type",ctypes.c_uint),("u",_U)]

def type_unicode(s):
    for ch in s:
        for up in (False,True):
            inp=INPUT(type=INPUT_KEYBOARD)
            inp.u.ki=KEYBDINPUT(wScan=ord(ch),dwFlags=KEYEVENTF_UNICODE|(KEYEVENTF_KEYUP if up else 0))
            user32.SendInput(1,ctypes.byref(inp),ctypes.sizeof(INPUT))

def vlist(arr): return [arr.GetElement(i) for i in range(arr.Length)]
def snap():
    sws=client.CreateObject(SHDocVw.ShellWindows,interface=SHDocVw.IShellWindows); d={}
    for i in range(sws.Count):
        w=sws.Item(i)
        try:url=w.LocationURL
        except Exception:url=""
        try:h=w.HWND
        except Exception:h=0
        d.setdefault(h,[]).append(url)
    return d
def close_hwnd(h): user32.PostMessageW(h,0x0010,0,0)
def find_button(root,aid):
    c=uia.CreatePropertyCondition(UIA.UIA_ControlTypePropertyId,UIA.UIA_ButtonControlTypeId)
    for b in vlist(root.FindAll(UIA.TreeScope_Descendants,c)):
        if (b.CurrentAutomationId or "")==aid: return b
def invoke(e):
    e.GetCurrentPattern(UIA.UIA_InvokePatternId).QueryInterface(UIA.IUIAutomationInvokePattern).Invoke()

X=r"C:\Users\kibod\AppData\Local\Temp\opencode\projects\tests"
Y=r"C:\Users\kibod\AppData\Local\Temp\opencode\scratch"

start=set(snap().keys())
subprocess.Popen(["explorer.exe",X]); time.sleep(2.5)
wh=list(set(snap().keys())-start)[0]
fg=user32.GetForegroundWindow()
print("wh=%s foreground=%s same=%s" % (wh,fg,wh==fg))
root=uia.ElementFromHandle(wh)

invoke(find_button(root,"AddButton")); time.sleep(1.0)
print("after add:", snap().get(wh))

# раскрыть все TextBox (адресная строка и поиск)
ec=uia.CreatePropertyCondition(UIA.UIA_ControlTypePropertyId,UIA.UIA_EditControlTypeId)
print("--- TextBoxes ---")
for e in vlist(root.FindAll(UIA.TreeScope_Descendants,ec)):
    nm=e.CurrentName; aid=e.CurrentAutomationId
    val=None
    try:
        vp=e.GetCurrentPattern(UIA.UIA_ValuePatternId).QueryInterface(UIA.IUIAutomationValuePattern)
        val=vp.CurrentValue
    except Exception as ex: val="ERR"
    print("  name=%r aid=%r value=%r" % (nm,aid,val))

# фокус на первый TextBox aid==TextBox (адресная строка), ввод символа
target=None
for e in vlist(root.FindAll(UIA.TreeScope_Descendants,ec)):
    if (e.CurrentAutomationId or "")=="TextBox":
        target=e; break
print("target addr bar:", target.CurrentName if target else None)
if target:
    target.SetFocus(); time.sleep(0.4)
    fg2=user32.GetForegroundWindow()
    print("fg after setfocus:", fg2, "== wh:", fg2==wh)
    type_unicode("Z")
    time.sleep(0.4)
    # перечитать значение адресной строки
    try:
        vp=target.GetCurrentPattern(UIA.UIA_ValuePatternId).QueryInterface(UIA.IUIAutomationValuePattern)
        print("addr value after typing Z:", repr(vp.CurrentValue))
    except Exception as ex:
        print("re-read err", repr(ex))

close_hwnd(wh); print("closed", wh)
