"""Разведка: ShellWindows + UIA-вкладки Проводника (Win11).

Печатает:
 1) все окна из SHDocVw.ShellWindows (класс, hwnd, путь, геометрия, состояние);
 2) для файловых окон — вкладки через UIA (Title + CurrentIsSelected);
 3) пробуем прочитать путь вкладки БЕЗ переключения (подсказка/значение).
"""
import sys
import json
import time
import ctypes

import comtypes
from comtypes import client

# --- COM init (STA) ---
comtypes.CoInitialize()

SHDocVw = client.GetModule("shdocvw.dll")
UIA = client.GetModule("UIAutomationCore.dll")

log = []


def p(*a):
    s = " ".join(str(x) for x in a)
    log.append(s)
    print(s)


# --- 1. ShellWindows ---
sws = client.CreateObject(SHDocVw.ShellWindows, interface=SHDocVw.IShellWindows)
count = sws.Count
p("ShellWindows count =", count)

uia = UIA.CUIAutomation()
FILE_CLASSES = {"CabinetWClass", "ExploreWClass"}


def variant_to_list(safe_array):
    """IUIAutomationElementArray -> python list."""
    out = []
    n = safe_array.Length
    for i in range(n):
        out.append(safe_array.GetElement(i))
    return out


for i in range(count):
    w = sws.Item(i)
    try:
        cls = w.FullName  # not class; use GetClass via IOleWindow? fallback
    except Exception:
        cls = "?"
    hwnd = None
    try:
        hwnd = w.HWND
    except Exception as e:
        hwnd = "ERR:%r" % e

    loc_url = ""
    loc_name = ""
    path = ""
    try:
        loc_url = w.LocationURL
    except Exception:
        pass
    try:
        loc_name = w.LocationName
    except Exception:
        pass
    try:
        doc = w.Document
        if doc is not None:
            folder = doc.Folder
            path = folder.Self.Path
    except Exception as e:
        path = "ERR:%r" % e

    # geometry
    geom = {}
    for attr in ("Left", "Top", "Width", "Height", "WindowState"):
        try:
            geom[attr] = getattr(w, attr)
        except Exception as e:
            geom[attr] = "ERR"

    # class name via GetClassName
    clsname = ""
    if isinstance(hwnd, int) and hwnd:
        buf = ctypes.create_unicode_buffer(256)
        ctypes.windll.user32.GetClassNameW(hwnd, buf, 256)
        clsname = buf.value

    p("[%d] hwnd=%s cls=%r loc=%r name=%r path=%r geom=%s" % (
        i, hwnd, clsname, loc_url, loc_name, path, geom))

    # --- 2. UIA tabs for file windows ---
    if clsname in FILE_CLASSES and isinstance(hwnd, int) and hwnd:
        try:
            root = uia.ElementFromHandle(hwnd)
            cond = uia.CreatePropertyCondition(
                UIA.UIA_ControlTypePropertyId, UIA.UIA_TabItemControlTypeId)
            arr = root.FindAll(UIA.TreeScope_Descendants, cond)
            tabs = variant_to_list(arr)
            p("    tabs:", len(tabs))
            for ti, t in enumerate(tabs):
                title = t.CurrentName
                sel = t.CurrentIsSelected
                # try to read a path hint without selecting
                hint = ""
                try:
                    vp = t.GetCurrentPattern(UIA.UIA_ValuePatternId)
                    hint = "value=%r" % vp.CurrentValue
                except Exception:
                    pass
                ht = ""
                try:
                    ht = t.CurrentHelpText
                except Exception:
                    pass
                p("      tab[%d] sel=%s title=%r help=%r %s" % (
                    ti, sel, title, ht, hint))
        except Exception as e:
            p("    UIA ERR %r" % (e,))

# save
out = r"C:\Users\kibod\AppData\Local\Temp\opencode\projects\tests\out\probe_explorer.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump({"log": log}, f, ensure_ascii=False, indent=2)
p("saved ->", out)
