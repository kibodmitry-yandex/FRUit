"""FRUit — ядро: съём и восстановление окон/вкладок Проводника.

Модель:
  * Каждое окно Проводника = группа записей ShellWindows с общим HWND.
  * Каждая вкладка = отдельная запись со своим «уникальным адресом»
    (файловый путь или виртуальная папка).
  * Геометрия окна читается через GetWindowPlacement/GetWindowRect.

Восстановление надёжное:
  * первая вкладка окна открывается через SHOpenFolderAndSelectItems;
  * остальные вкладки добавляются Invoke кнопки «Add New Tab» и навигируются
    адресно через IWebBrowser2.Navigate (без «хлебных крошек» и клавиатуры);
  * если добавление вкладки не удалось — папка открывается отдельным окном
    (откат), чтобы ни одна папка не потерялась.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import List, Optional

import comtypes
from comtypes import client

from . import tabs as tabops
from . import winapi

# HWND, для которых ShellWindows возвращает «не файловые» окна (не трогаем)
_FILE_CLASSES = {"CabinetWClass", "ExploreWClass"}


@dataclass
class Tab:
    """Одна вкладка (её уникальный адрес)."""
    path: Optional[str]      # файловый путь или None для виртуальных
    name: str = ""           # отображаемое имя
    virtual: bool = False    # виртуальная папка (This PC, Быстрый доступ…)
    url: str = ""            # исходный file:// URL (для отладки)


@dataclass
class Window:
    """Окно Проводника со своими вкладками и геометрией."""
    tabs: List[Tab] = field(default_factory=list)
    active: int = 0                     # индекс активной вкладки
    geometry: Optional[winapi.WindowGeometry] = None


def _shell_windows():
    comtypes.CoInitialize()
    SHDocVw = client.GetModule("shdocvw.dll")
    return client.CreateObject(
        SHDocVw.ShellWindows, interface=SHDocVw.IShellWindows)


def _window_class(hwnd: int) -> str:
    import ctypes
    buf = ctypes.create_unicode_buffer(256)
    ctypes.windll.user32.GetClassNameW(hwnd, buf, 256)
    return buf.value


def capture_state() -> List[Window]:
    """Снимает текущие окна Проводника со всеми вкладками."""
    sws = _shell_windows()
    order: List[int] = []          # hwnd в порядке появления
    grouped: dict = {}             # hwnd -> [Tab]

    for i in range(sws.Count):
        item = sws.Item(i)
        try:
            hwnd = int(item.HWND)
        except Exception:
            continue
        if not hwnd:
            continue
        cls = _window_class(hwnd)
        if cls not in _FILE_CLASSES:
            continue  # пропускаем рабочий стол/прочее

        try:
            url = item.LocationURL or ""
        except Exception:
            url = ""
        try:
            name = item.LocationName or ""
        except Exception:
            name = ""

        path, virtual = winapi.url_to_path(url)
        tab = Tab(path=path, name=name, virtual=virtual, url=url)

        if hwnd not in grouped:
            grouped[hwnd] = []
            order.append(hwnd)
        grouped[hwnd].append(tab)

    windows: List[Window] = []
    for hwnd in order:
        tablist = grouped[hwnd]
        if not tablist:
            continue
        active = tabops.selected_tab_index(hwnd)
        if active is None or active < 0 or active >= len(tablist):
            active = 0
        geo = winapi.get_window_geometry(hwnd)
        windows.append(Window(tabs=tablist, active=active, geometry=geo))

    return windows


def _find_window_hwnd_by_path(path: str, timeout: float = 6.0) -> Optional[int]:
    """Ждёт появления окна с первой папкой и возвращает его HWND."""
    target = path.replace("/", "\\").lower().rstrip("\\")
    deadline = time.time() + timeout
    while time.time() < deadline:
        sws = _shell_windows()
        for i in range(sws.Count):
            item = sws.Item(i)
            try:
                url = item.LocationURL or ""
            except Exception:
                continue
            p, _ = winapi.url_to_path(url)
            if p and p.replace("/", "\\").lower().rstrip("\\") == target:
                try:
                    return int(item.HWND)
                except Exception:
                    return None
        time.sleep(0.2)
    return None


def _navigate_new_tab(hwnd: int, path: str, timeout: float = 4.0) -> bool:
    """Добавляет вкладку и навигирует её по пути. True — вкладка открылась.

    Сначала Invoke «Add New Tab», затем находим появившуюся ПУСТУЮ вкладку
    в ShellWindows и навигируем именно её через Navigate(path).
    """
    if not tabops.click_add_button(hwnd):
        return False

    # ждём появления пустой вкладки и навигируем её
    deadline = time.time() + timeout
    while time.time() < deadline:
        sws = _shell_windows()
        for i in range(sws.Count):
            item = sws.Item(i)
            try:
                if int(item.HWND) == hwnd and (item.LocationURL or "") == "":
                    item.Navigate(path)
                    # подтверждение: вкладка должна перестать быть пустой
                    if _wait_tab_location(hwnd, path, timeout=3.0):
                        return True
                    return False
            except Exception:
                continue
        time.sleep(0.15)
    return False


def _wait_tab_location(hwnd: int, path: str, timeout: float = 3.0) -> bool:
    """Подтверждает, что среди вкладок окна появился указанный путь."""
    target = path.replace("/", "\\").lower().rstrip("\\")
    deadline = time.time() + timeout
    while time.time() < deadline:
        sws = _shell_windows()
        for i in range(sws.Count):
            item = sws.Item(i)
            try:
                if int(item.HWND) == hwnd:
                    p, _ = winapi.url_to_path(item.LocationURL or "")
                    if p and p.replace("/", "\\").lower().rstrip("\\") == target:
                        return True
            except Exception:
                continue
        time.sleep(0.2)
    return False


def restore_state(windows: List[Window], group_tabs: bool = True,
                  pause: float = 0.4) -> dict:
    """Восстанавливает окна. Возвращает сводку {opened, tabs, fallback}.

    group_tabs=True — вкладки одного окна собираются обратно в одно окно;
    иначе каждая папка открывается отдельным окном (просто и максимально
    надёжно).
    """
    summary = {"opened": 0, "tabs": 0, "fallback": 0}
    first_hwnds: List[int] = []

    for win in windows:
        real_tabs = [t for t in win.tabs if not t.virtual and t.path]
        if not real_tabs:
            continue

        # первая вкладка -> окно
        first = real_tabs[0]
        winapi.launch_folder(first.path)
        summary["opened"] += 1
        hwnd = None
        if group_tabs:
            hwnd = _find_window_hwnd_by_path(first.path)

        if hwnd is None:
            # не нашли окно или группировка выключена — открываем остальные
            # как отдельные окна
            for t in real_tabs[1:]:
                winapi.launch_folder(t.path)
                summary["opened"] += 1
            continue

        first_hwnds.append(hwnd)
        summary["tabs"] += 1  # первая вкладка

        # остальные вкладки -> в то же окно
        for t in real_tabs[1:]:
            if _navigate_new_tab(hwnd, t.path):
                summary["tabs"] += 1
            else:
                winapi.launch_folder(t.path)  # откат: отдельным окном
                summary["opened"] += 1
                summary["fallback"] += 1

        time.sleep(pause)

    # геометрия и активная вкладка — по окнам, которые удалось сгруппировать
    restored = [w for w in windows]
    _apply_geometry_and_active(windows, group_tabs)

    return summary


def _apply_geometry_and_active(windows: List[Window], group_tabs: bool) -> None:
    """Применяет геометрию и активную вкладку к восстановленным окнам."""
    for win in windows:
        real_tabs = [t for t in win.tabs if not t.virtual and t.path]
        if not real_tabs:
            continue
        hwnd = _find_window_hwnd_by_path(real_tabs[0].path, timeout=3.0)
        if hwnd is None:
            continue
        if win.geometry:
            winapi.set_window_geometry(hwnd, win.geometry)
        if group_tabs and 0 <= win.active < len(real_tabs):
            tabops.select_tab(hwnd, win.active)
