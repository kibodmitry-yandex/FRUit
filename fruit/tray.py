"""FRUit — режим трея: иконка «стек папок», контекстное меню и горячие клавиши.

Контекстное меню (правый клик по значку):
  * Сделать снапшот  — запомнить текущие группы вкладок и окна (дедупликация:
    полные дубли групп/окон не добавляются повторно);
  * Восстановить все — открыть все запомненные раскладки;
  * список запомненных раскладок: группы вкладок — по первой вкладке
    (маркер 🗂), отдельные окна — своим маркером (🗀); у каждого — подменю
    «Восстановить» и «✕ Удалить»;
  * Папка данных, Выход.

Меню обновляется СРАЗУ после изменений: pystray строит HMENU один раз и на
правый клик переиспользует его, callable-меню сам не пересчитывает — поэтому
после снапшота/удаления явно вызывается icon.update_menu().
"""

from __future__ import annotations

import os
import subprocess
import threading

import pystray
from pynput import keyboard

from . import core, groups
from .icons import (DELETE_GLYPH, GROUP_GLYPH, WINDOW_GLYPH, app_icon)

_LOCK = threading.Lock()          # защита от параллельного съёма/восстановления
_ICON = None                      # pystray.Icon, ставится в run()

HOTKEY_SAVE = "<ctrl>+<alt>+s"
HOTKEY_RESTORE = "<ctrl>+<alt>+r"


def _log(msg: str) -> None:
    try:
        print(f"[FRUit] {msg}", flush=True)
    except Exception:
        pass


def _refresh() -> None:
    """Сразу обновляет и меню, и всплывающую подсказку значка.

    update_menu() перестраивает только HMENU; подсказка (icon.title) — это
    отдельное поле, и сама по себе она не пересчитывается (см. шапку модуля).
    """
    ic = _ICON
    if ic is None:
        return
    try:
        ic.title = _tooltip()
    except Exception:
        pass
    try:
        ic.update_menu()
    except Exception:
        pass


def _async(fn) -> None:
    """Выполняет fn() в фоне под общим замком (трей не «замерзает»)."""
    def runner():
        with _LOCK:
            try:
                fn()
            except Exception as e:
                _log(f"ошибка: {e}")
    threading.Thread(target=runner, daemon=True).start()


# --- действия --------------------------------------------------------------

def make_snapshot() -> str:
    """Запоминает текущие группы/окна, пропуская полные дубли."""
    windows = core.capture_state()
    added, skipped = groups.add_state(windows)
    _log(f"снапшот: добавлено {added}, дублей пропущено {skipped}")
    if added:
        _refresh()                      # <- меню обновится сразу
    return f"+{added} (дублей {skipped})"


def restore_all() -> None:
    windows = groups.all_windows()
    if not windows:
        _log("нет запомненных раскладок")
        return
    summary = core.restore_state(windows)
    _log(f"восстановлено: окон {summary['opened']}, вкладок {summary['tabs']}")


def restore_entry(entry_id: str) -> None:
    win = groups.entry_window(entry_id)
    if win is None:
        return
    core.restore_state([win])


def delete_entry(entry_id: str) -> None:
    groups.remove(entry_id)
    _log(f"удалена запись {entry_id}")
    _refresh()                          # <- список сократится сразу


def _open_data_dir() -> None:
    subprocess.Popen(["explorer.exe", os.path.dirname(groups.store_path())])


# --- сборка меню -----------------------------------------------------------

def _entry_text(e: dict) -> str:
    kind = e.get("kind", "window")
    label = e.get("label", "?")
    n = len(e.get("tabs", []))
    glyph = GROUP_GLYPH if kind == "group" else WINDOW_GLYPH
    if kind == "group":
        return f"{glyph} {label} ({n} вкл)"
    return f"{glyph} {label}"


def _entry_item(e: dict) -> pystray.MenuItem:
    eid = e.get("id")
    sub = pystray.Menu(
        pystray.MenuItem("Восстановить", (lambda i=eid: _async(lambda: restore_entry(i)))),
        pystray.MenuItem(f"{DELETE_GLYPH} Удалить", (lambda i=eid: _async(lambda: delete_entry(i)))),
    )
    return pystray.MenuItem(_entry_text(e), sub)


def _menu_items(icon):
    items = [
        pystray.MenuItem("Сделать снапшот", (lambda: _async(make_snapshot)), default=True),
        pystray.MenuItem("Восстановить все", (lambda: _async(restore_all))),
        pystray.Menu.SEPARATOR,
    ]

    entries = groups.load()
    entries.sort(key=lambda e: (e.get("kind") != "group", -e.get("created", 0)))
    if not entries:
        items.append(pystray.MenuItem("(нет запомненных раскладок)", None, enabled=False))
    for e in entries:
        items.append(_entry_item(e))

    items.append(pystray.Menu.SEPARATOR)
    items.append(pystray.MenuItem("Папка данных", _open_data_dir))
    items.append(pystray.MenuItem("Выход", (lambda: icon.stop())))
    return items


def _make_menu(icon):
    return pystray.Menu(lambda: _menu_items(icon))


def _tooltip() -> str:
    return f"FRUit — запомнено раскладок: {len(groups.load())}"


# --- запуск ----------------------------------------------------------------

def run() -> None:
    global _ICON
    icon = pystray.Icon("fruit", app_icon(64), _tooltip())
    icon.menu = _make_menu(icon)
    _ICON = icon
    _log(f"трей запущен, раскладок: {len(groups.load())}")
    listener = keyboard.GlobalHotKeys({
        HOTKEY_SAVE: (lambda: _async(make_snapshot)),
        HOTKEY_RESTORE: (lambda: _async(restore_all)),
    })
    listener.daemon = True
    listener.start()

    icon.run()  # блокирующий цикл сообщений


if __name__ == "__main__":
    run()
