"""FRUit — операции над вкладками Проводника через UI Automation.

Единственное место, где используется UIA, — создание новой вкладки
(Invoke кнопки «Add New Tab») и выбор вкладки. Навигация вкладки по пути
делается в core.py через IWebBrowser2.Navigate, а не «хлебными крошками».
"""

from __future__ import annotations

import time
from typing import List, Optional

import comtypes
from comtypes import client

# модуль с константами/интерфейсами UIA (генерируется comtypes)
_UIA = None
_uia = None


def _ensure_uia():
    """Ленивая инициализация CUIAutomation (потокобезопасно по замыканию)."""
    global _UIA, _uia
    if _uia is None:
        comtypes.CoInitialize()
        _UIA = client.GetModule("UIAutomationCore.dll")
        _uia = client.CreateObject(
            _UIA.CUIAutomation, interface=_UIA.IUIAutomation)
    return _uia, _UIA


def _vlist(arr) -> List:
    return [arr.GetElement(i) for i in range(arr.Length)]


def _find_buttons(root, uia, UIA):
    cond = uia.CreatePropertyCondition(
        UIA.UIA_ControlTypePropertyId, UIA.UIA_ButtonControlTypeId)
    return _vlist(root.FindAll(uia, ) if False else root.FindAll(
        UIA.TreeScope_Descendants, cond))


def _tab_items(root, uia, UIA) -> List:
    cond = uia.CreatePropertyCondition(
        UIA.UIA_ControlTypePropertyId, UIA.UIA_TabItemControlTypeId)
    return _vlist(root.FindAll(UIA.TreeScope_Descendants, cond))


def click_add_button(hwnd: int, wait: float = 0.6) -> bool:
    """Invoke кнопки «Add New Tab» (AutomationId='AddButton') в окне.

    Возвращает True, если кнопка найдена и нажата (новая вкладка создана).
    """
    uia, UIA = _ensure_uia()
    try:
        root = uia.ElementFromHandle(hwnd)
    except Exception:
        return False
    btn = None
    for b in _find_buttons(root, uia, UIA):
        if (b.CurrentAutomationId or "") == "AddButton":
            btn = b
            break
    if btn is None:
        return False
    try:
        pat = btn.GetCurrentPattern(UIA.UIA_InvokePatternId)
        pat.QueryInterface(UIA.IUIAutomationInvokePattern).Invoke()
    except Exception:
        return False
    time.sleep(wait)
    return True


def selected_tab_index(hwnd: int) -> Optional[int]:
    """Индекс выбранной (активной) вкладки в окне; None — если не найден."""
    uia, UIA = _ensure_uia()
    try:
        root = uia.ElementFromHandle(hwnd)
    except Exception:
        return None
    for i, t in enumerate(_tab_items(root, uia, UIA)):
        try:
            if t.CurrentIsSelected:
                return i
        except Exception:
            continue
    return None


def select_tab(hwnd: int, index: int, wait: float = 0.3) -> bool:
    """Делает вкладку с индексом `index` активной (SelectionItem.Select)."""
    uia, UIA = _ensure_uia()
    try:
        root = uia.ElementFromHandle(hwnd)
    except Exception:
        return False
    items = _tab_items(root, uia, UIA)
    if index < 0 or index >= len(items):
        return False
    try:
        pat = items[index].GetCurrentPattern(UIA.UIA_SelectionItemPatternId)
        pat.QueryInterface(UIA.IUIAutomationSelectionItemPattern).Select()
        time.sleep(wait)
        return True
    except Exception:
        return False


def tab_count(hwnd: int) -> int:
    """Число вкладок в окне (для проверки, что вкладка реально добавилась)."""
    uia, UIA = _ensure_uia()
    try:
        root = uia.ElementFromHandle(hwnd)
    except Exception:
        return 0
    return len(_tab_items(root, uia, UIA))
