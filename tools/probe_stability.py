import os, time, ctypes, subprocess
import comtypes
from comtypes import client
comtypes.CoInitialize()
UIA = client.GetModule("UIAutomationCore.dll")
SHDocVw = client.GetModule("shdocvw.dll")
user32 = ctypes.windll.user32
uia = client.CreateObject(UIA.CUIAutomation, interface=UIA.IUIAutomation)

def vlist(a): return [a.GetElement(i) for i in range(a.Length)]
def snap():
    sws = client.CreateObject(SHDocVw.ShellWindows, interface=SHDocVw.IShellWindows); d={}
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

# --- текущие окна (остатки?) ---
cur = snap()
print("EXISTING windows now:")
for h,us in cur.items(): print("  hwnd=%s n=%d %s" % (h,len(us),us))

X=r"C:\Users\kibod\AppData\Local\Temp\opencode\projects\tests"
Y=r"C:\Users\kibod\AppData\Local\Temp\opencode\scratch"

start=set(cur.keys())
subprocess.Popen(["explorer.exe",X]); time.sleep(2.5)
newh=set(snap().keys())-start
wh=list(newh)[0]
root=uia.ElementFromHandle(wh)
print("\nopened test", wh)

invoke(find_button(root,"AddButton")); time.sleep(1.0)
print("after add:", snap().get(wh))

# navigate пустую вкладку
target=None
for i in range(sws_n if False else 0): pass
sws=client.CreateObject(SHDocVw.ShellWindows,interface=SHDocVw.IShellWindows)
for i in range(sws.Count):
    w=sws.Item(i)
    try:
        if w.HWND==wh and w.LocationURL=="":
            target=w; break
    except Exception: pass
print("empty tab found:", target is not None)
if target:
    target.Navigate(Y)

# наблюдение стабильности с дефокусом
for t in (1,2,3,4,5,6,8):
    time.sleep(1 if t==1 else (t - prev if False else 1))
    prev=t
    s=snap().get(wh,[])
    print("  t=%ds tabs=%d %s" % (t,len(s),s))

# дефokus: свернуть наше тестовое окно и посмотреть ещё раз
user32.ShowWindow(wh, 6)  # SW_MINIMIZE
time.sleep(2)
s=snap().get(wh,[])
print("  after minimize tabs=%d %s" % (len(s),s))

close_hwnd(wh); print("closed test", wh)
