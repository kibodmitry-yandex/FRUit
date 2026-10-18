"""FRUit — низкоуровневые помощники Windows (ctypes).

Здесь только «чистый» Win32 без COM: геометрия окна, открытие папки
через SHOpenFolderAndSelectItems, разбор file:// URL.
COM-перечисление окон Проводника живёт в core.py.
"""

from __future__ import annotations

import ctypes
import os
import subprocess
from ctypes import wintypes
from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple
from urllib.parse import unquote, urlparse

user32 = ctypes.windll.user32
shell32 = ctypes.windll.shell32
ole32 = ctypes.windll.ole32

# --- константы ---
SW_SHOWNORMAL = 1
SW_SHOWMINIMIZED = 2
SW_SHOWMAXIMIZED = 3
SW_MINIMIZE = 6
SW_SHOWMINNOACTIVE = 7
SW_RESTORE = 9
SW_SHOW = 5

SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOZORDER = 0x0004
SWP_NOACTIVATE = 0x0010
SWP_SHOWWINDOW = 0x0040

HWND_TOP = 0

COINIT_APARTMENTTHREADED = 0x2


# --- структуры для WINDOWPLACEMENT ---
class RECT(ctypes.Structure):
    _fields_ = [("left", wintypes.LONG), ("top", wintypes.LONG),
                ("right", wintypes.LONG), ("bottom", wintypes.LONG)]


class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]


class WINDOWPLACEMENT(ctypes.Structure):
    _fields_ = [
        ("length", wintypes.UINT),
        ("flags", wintypes.UINT),
        ("showCmd", wintypes.UINT),
        ("ptMinPosition", POINT),
        ("ptMaxPosition", POINT),
        ("rcNormalPosition", RECT),
    ]


@dataclass
class WindowGeometry:
    """Геометрия окна Проводника для восстановления."""
    left: int
    top: int
    width: int
    height: int
    state: str  # "normal" | "max" | "min"


def com_init() -> None:
    """Инициализация COM для текущего потока (STA). Идемпотентна."""
    ole32.CoInitializeEx(None, COINIT_APARTMENTTHREADED)


def get_window_geometry(hwnd: int) -> Optional[WindowGeometry]:
    """Читает геометрию и состояние окна. Для свёрнутых/развёрнутых
    берёт «нормальный» прямоугольник, чтобы восстановить именно его."""
    if not hwnd or not user32.IsWindow(hwnd):
        return None

    iconic = user32.IsIconic(hwnd)
    zoomed = user32.IsZoomed(hwnd)
    if zoomed:
        state = "max"
    elif iconic:
        state = "min"
    else:
        state = "normal"

    if state == "normal":
        r = RECT()
        if not user32.GetWindowRect(wintypes.HWND(hwnd), ctypes.byref(r)):
            return None
        return WindowGeometry(r.left, r.top, r.right - r.left, r.bottom - r.top, state)

    # для max/min — нормальный прямоугольник из WINDOWPLACEMENT
    wp = WINDOWPLACEMENT()
    wp.length = ctypes.sizeof(WINDOWPLACEMENT)
    if not user32.GetWindowPlacement(wintypes.HWND(hwnd), ctypes.byref(wp)):
        return None
    r = wp.rcNormalPosition
    return WindowGeometry(r.left, r.top, r.right - r.left, r.bottom - r.top, state)


def set_window_geometry(hwnd: int, geo: WindowGeometry) -> bool:
    """Восстанавливает позицию/размер/состояние окна."""
    if not hwnd or not user32.IsWindow(hwnd):
        return False

    # сначала вернуть из свёрнутого/развёрнутого в нормальное
    user32.ShowWindow(wintypes.HWND(hwnd), SW_RESTORE)

    user32.SetWindowPos(
        wintypes.HWND(hwnd), wintypes.HWND(HWND_TOP),
        geo.left, geo.top, geo.width, geo.height,
        SWP_NOZORDER | SWP_NOACTIVATE,
    )

    if geo.state == "max":
        user32.ShowWindow(wintypes.HWND(hwnd), SW_SHOWMAXIMIZED)
    # "min" и "normal" оставляем нормальным окном (видимым)
    return True


def url_to_path(url: str) -> Tuple[Optional[str], bool]:
    """file:// URL -> файловый путь.

    Возвращает (путь, виртуальная_ли). Для виртуальных папок (This PC,
    Быстрый доступ и т.п.) file-URL нет — путь None, флаг True.
    """
    if not url:
        return None, True
    parsed = urlparse(url)
    if parsed.scheme == "file":
        path = unquote(parsed.path)
        # на Windows путь вида /C:/Users/... -> C:/Users/...
        if path.startswith("/") and len(path) > 2 and path[2] == ":":
            path = path[1:]
        return path.replace("/", os.sep), False
    # не-file схема (ftp, virtual и т.п.)
    return None, True


# --- настройки прототипов ---
shell32.ILCreateFromPathW.argtypes = [wintypes.LPCWSTR]
shell32.ILCreateFromPathW.restype = ctypes.c_void_p
shell32.SHOpenFolderAndSelectItems.argtypes = [
    ctypes.c_void_p, ctypes.c_uint, ctypes.c_void_p, wintypes.DWORD]
shell32.SHOpenFolderAndSelectItems.restype = wintypes.BOOL
shell32.ILFree.argtypes = [ctypes.c_void_p]


def launch_folder(path: str) -> bool:
    """Открывает папку как НОВОЕ окно Проводника через explorer.exe.

    Самый надёжный способ открыть именно новое окно (для группировки вкладок).
    """
    if not path:
        return False
    try:
        subprocess.Popen(["explorer.exe", path])
        return True
    except Exception:
        return False


def open_folder(path: str, select: Optional[Iterable[str]] = None) -> bool:
    """Открывает папку в Проводнике (документированный SHOpenFolderAndSelectItems).

    `select` — имена объектов внутри папки, которые нужно выделить.
    Для виртуальных/непростых падений тихо возвращает False.
    """
    if not path:
        return False
    folder_pidl = shell32.ILCreateFromPathW(path)
    if not folder_pidl:
        return False
    try:
        child_pidls: List[int] = []
        if select:
            for name in select:
                full = os.path.join(path, name)
                cp = shell32.ILCreateFromPathW(full)
                if cp:
                    child_pidls.append(cp)
        if child_pidls:
            arr = (ctypes.c_void_p * len(child_pidls))(*child_pidls)
            ok = shell32.SHOpenFolderAndSelectItems(
                folder_pidl, len(child_pidls), arr, 0)
            for cp in child_pidls:
                shell32.ILFree(ctypes.c_void_p(cp))
        else:
            ok = shell32.SHOpenFolderAndSelectItems(folder_pidl, 0, None, 0)
        return bool(ok)
    finally:
        shell32.ILFree(ctypes.c_void_p(folder_pidl))
