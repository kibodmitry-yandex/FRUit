"""FRUit — режим трея: иконка «стек папок», контекстное меню и горячие клавиши.

Контекстное меню (правый клик по значку):
  * Сделать снапшот  — запомнить текущие группы вкладок и окна (дедупликация:
    полные дубли групп/окон не добавляются повторно);
  * Восстановить все — открыть все запомненные раскладки;
  * список запомненных раскладок: группы вкладок — по первой вкладке
    (маркер 🗂), отдельные окна — своим маркером (🗀); у каждого — подменю,
    где СВЕРХУ состав записи (пункты только для чтения: что именно откроет
    «Восстановить»), ниже — «Восстановить» и «✕ Удалить»; см. _entry_item();
  * Папка данных, Выход.

Меню обновляется СРАЗУ после изменений: pystray строит HMENU один раз и на
правый клик переиспользует его, callable-меню сам не пересчитывает — поэтому
после снапшота/удаления явно вызывается icon.update_menu().

ЛОВУШКА pystray: число параметров обработчика пункта меню ЗАДАЁТ способ
вызова (MenuItem._assert_action): 0 — action(), 1 — action(icon),
2 — action(icon, item). Поэтому замыкание вида ``lambda i=eid: ...`` (один
параметр!) получит в i САМ ЗНАЧОК, а не id записи — см. _entry_item().

ЛОВУШКА Win32: в тексте пункта ``&`` помечает ускоряющую клавишу, поэтому
амперсанды удваиваются — см. _menu_text(). Текст попадает в InsertMenuItem
как есть, без обработки со стороны pystray.
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
    """Восстанавливает одну запись (окно/группу) по id."""
    win = groups.entry_window(entry_id)
    if win is None:
        _log(f"восстановление не удалось: запись {entry_id!r} не найдена")
        return
    tabs = len(win.tabs)
    summary = core.restore_state([win])
    _log(f"восстановлена запись {entry_id}: окон {summary['opened']}, "
         f"вкладок {summary['tabs']} (в записи {tabs})")


def delete_entry(entry_id: str) -> None:
    """Удаляет запись по id и сразу обновляет меню с подсказкой."""
    if groups.remove(entry_id):
        _log(f"удалена запись {entry_id}")
    else:
        _log(f"удаление не удалось: запись {entry_id!r} не найдена")
    _refresh()


def _open_data_dir() -> None:
    subprocess.Popen(["explorer.exe", os.path.dirname(groups.store_path())])


# --- сборка меню -----------------------------------------------------------

# Превью состава записи в подменю: сколько вкладок показывать и как их помечать.
PREVIEW_MAX = 12              # длинные группы обрезаем, чтобы меню не разрасталось
PREVIEW_INDENT = "    "       # визуальный отступ строк состава
PREVIEW_BULLET = "•"          # маркер строки состава


def _menu_text(text: str) -> str:
    """Готовит текст для пункта меню Win32.

    В меню ``&`` — это префикс ускоряющей клавиши, а не символ: папка
    «Prog & Data» превратилась бы в «Prog  Data» с подчёркнутой буквой.
    Чтобы показать амперсанд буквально, его удваивают (``&&``). pystray
    передаёт текст в AppendMenu/InsertMenuItem без обработки, поэтому
    экранируем сами.
    """
    return str(text).replace("&", "&&")


def _entry_text(e: dict) -> str:
    kind = e.get("kind", "window")
    label = e.get("label", "?")
    n = len(e.get("tabs", []))
    glyph = GROUP_GLYPH if kind == "group" else WINDOW_GLYPH
    if kind == "group":
        return _menu_text(f"{glyph} {label} ({n} вкл)")
    return _menu_text(f"{glyph} {label}")


def _preview_lines(e: dict) -> list:
    """Строки состава записи — что именно откроет «Восстановить».

    Показываем имена вкладок, а где имя неоднозначно (в группе есть папки с
    одинаковым именем) или вкладка одна — полный путь/адрес: иначе по имени
    непонятно, какая из них какая. Длинные группы обрезаем (PREVIEW_MAX).
    Эти строки уходят в подменю как пункты только для чтения (см. _entry_item).
    """
    tabs = e.get("tabs") or []
    if not tabs:
        return []

    def short(t: dict) -> str:
        return t.get("name") or t.get("path") or t.get("url") or "без имени"

    def full(t: dict) -> str:
        return t.get("path") or t.get("url") or short(t)

    single = len(tabs) == 1
    names = [short(t) for t in tabs]
    repeated = set(n for n in names if names.count(n) > 1)

    texts = []
    for t, name in zip(tabs, names):
        if single or name in repeated:
            texts.append(full(t))
        else:
            texts.append(name)

    if len(texts) > PREVIEW_MAX:
        texts = texts[:PREVIEW_MAX] + ["… и ещё %d" % (len(texts) - PREVIEW_MAX)]

    return [PREVIEW_INDENT + PREVIEW_BULLET + " " + _menu_text(t) for t in texts]


def _entry_item(e: dict) -> pystray.MenuItem:
    """Пункт меню одной запомненной раскладки (заголовок + подменю).

    ВАЖНО: обработчики должны принимать НОЛЬ аргументов. pystray смотрит на
    число параметров функции (MenuItem._assert_action) и для 0 — вызывает
    action() без аргументов, для 1 — подставляет icon, для 2 — (icon, item).
    Поэтому «lambda i=eid: ...» (это ОДИН параметр!) получал в i сам значок
    pystray, а не id записи, и удаление молча ничего не делало. Замыкание
    через вложенную def с нулём аргументов сохраняет eid корректно.
    """
    eid = e.get("id")

    def do_restore():
        _async(lambda: restore_entry(eid))

    def do_delete():
        _async(lambda: delete_entry(eid))

    items = []
    # Состав записи — только чтение: без действия (action=None) и серым
    # (enabled=False → MFS_DISABLED в меню Win32), отделён от действий чертой.
    preview = _preview_lines(e)
    if preview:
        for line in preview:
            items.append(pystray.MenuItem(line, None, enabled=False))
        items.append(pystray.Menu.SEPARATOR)

    items.append(pystray.MenuItem("Восстановить", do_restore))
    items.append(pystray.MenuItem(f"{DELETE_GLYPH} Удалить", do_delete))

    return pystray.MenuItem(_entry_text(e), pystray.Menu(*items))


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
