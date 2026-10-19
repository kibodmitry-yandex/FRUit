"""Регрессия: пункты подменю трея («Восстановить» / «✕ Удалить») должны
получать ПРАВИЛЬНЫЙ id записи.

Баг (был): обработчики писались как ``lambda i=eid: ...`` — у такой лямбды
ОДИН параметр, а pystray (MenuItem._assert_action) для одного параметра
подставляет сам значок: ``action(icon)``. В итоге delete_entry()/restore_entry()
получали объект Icon вместо строки-id, и удаление молча ничего не делало
(groups.remove возвращает False, если id не найден).

Тест бьёт по реальному пути pystray: ``menu.items -> MenuItem -> item(icon)``,
то есть ровно то, что делает backend при клике. Данные — в
    `tools/out/test_tray_menu` (реальный %LOCALAPPDATA% не трогаем).
"""

import os
import sys

sys.path.insert(0, r"F:\FRUit")
os.environ["FRUIT_DATA"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "out", "test_tray_menu")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import pystray

from fruit import groups, tray
from fruit.icons import DELETE_GLYPH

ICON_CALLS = []


class FakeIcon(object):
    """Мини-замена pystray.Icon: только то, что трогает tray.py."""

    def __init__(self):
        self.title = ""
        self.menu = None

    def update_menu(self):
        ICON_CALLS.append("update_menu")

    def stop(self):
        ICON_CALLS.append("stop")


def _entry(eid, label, kind="window", n=1):
    return {
        "id": eid,
        "kind": kind,
        "label": label,
        "created": 1.0,
        "active": 0,
        "geometry": None,
        "tabs": [
            {"path": "C:\\%s%d" % (label, i), "name": label,
             "virtual": False, "url": ""}
            for i in range(n)
        ],
    }


def _entry_item_with(menu, needle):
    """Первый пункт верхнего уровня, в подменю которого есть `needle`."""
    for it in menu.items:
        sub = getattr(it, "submenu", None)
        if sub is None:
            continue
        texts = [getattr(s, "text", "") for s in sub.items]
        if any(needle in t for t in texts):
            return it, sub
    raise AssertionError("подменю с %r не найдено" % needle)


def _sub_item(sub, needle):
    for s in sub.items:
        if needle in getattr(s, "text", ""):
            return s
    raise AssertionError("пункта с %r нет" % needle)


def _click(menu_item, icon):
    """Ровно то, что делает pystray-бэкенд по клику."""
    menu_item(icon)


def main():
    groups.clear()
    groups._save([_entry("aaa", "ALFA"), _entry("bbb", "BETA", "group", 2)])

    icon = FakeIcon()
    tray._ICON = icon
    tray._async = lambda fn: fn()          # синхронно, без потоков

    restored = []
    tray.restore_entry = lambda eid: restored.append(eid)

    menu = tray._make_menu(icon)

    # --- состав записи: пункты только для чтения ВЫШЕ действий -------------
    parent, sub = _entry_item_with(menu, "Восстановить")
    sub_texts = [s.text for s in sub.items]
    read_only = [s for s in sub.items if not s.enabled]
    actions = [s for s in sub.items if s.enabled]

    assert len(read_only) == 2, \
        "ожидали 2 строки состава (2 вкладки), получили %r" % (sub_texts,)
    for s in read_only:
        assert s.submenu is None, "строка состава не должна иметь подменю"
        assert "C:\\BETA" in s.text, "в составе нет пути вкладки: %r" % s.text
    assert "Восстановить" in [s.text for s in actions]
    assert sub_texts.index(read_only[0].text) < sub_texts.index("Восстановить"), \
        "состав должен быть ВЫШЕ действий: %r" % (sub_texts,)
    print("состав записи (только чтение) над действиями: %r"
          % [s.text for s in read_only])

    # клик по строке состава ничего не делает и ничего не ломает
    state_before = groups.load()
    ICON_CALLS[:] = []
    _click(read_only[0], icon)
    assert groups.load() == state_before, "клик по составу что-то изменил"
    assert ICON_CALLS == [], "клик по составу ничего не должен запускать"

    # --- _preview_lines: дубли имён, одиночка, обрезка длинных групп -------
    two_same = _entry("dup", "DUP", "group", 2)          # имена вкладок совпадают
    lines = tray._preview_lines(two_same)
    assert len(lines) == 2 and all("C:\\DUP" in l for l in lines), lines

    one = _entry("one", "ONE")
    assert tray._preview_lines(one) == ["    • C:\\ONE0"], tray._preview_lines(one)

    many = _entry("many", "MANY", "group", tray.PREVIEW_MAX + 3)
    lines = tray._preview_lines(many)
    assert len(lines) == tray.PREVIEW_MAX + 1, len(lines)
    assert "… и ещё 3" in lines[-1], lines[-1]
    print("превью: дубли -> полные пути, одиночка -> путь, обрезка -> %r"
          % lines[-1])

    # амперсанд в имени папки не должен стать «ускоряющей клавишей»
    amp = {
        "id": "amp", "kind": "group", "label": "AMP", "created": 1.0,
        "active": 0, "geometry": None,
        "tabs": [
            {"path": "C:\\Prog & Data", "name": "Prog & Data",
             "virtual": False, "url": ""},
            {"path": "C:\\Other", "name": "Other", "virtual": False, "url": ""},
        ],
    }
    assert "Prog && Data" in tray._preview_lines(amp)[0], tray._preview_lines(amp)
    amp["label"] = "Prog & Data"          # и в заголовке записи тоже
    assert "Prog && Data" in tray._entry_text(amp), tray._entry_text(amp)
    print("амперсанд экранируется: %r" % tray._preview_lines(amp)[0])

    # --- Восстановить: id должен дойти до restore_entry -------------------
    parent, sub = _entry_item_with(menu, "Восстановить")
    _click(_sub_item(sub, "Восстановить"), icon)
    assert len(restored) == 1, "restore не вызвался: %r" % (restored,)
    got = restored[0]
    assert got in ("aaa", "bbb"), "в restore_entry ушёл не id: %r" % (got,)
    print("restore получил корректный id: %r (пункт %r)" % (got, parent.text))

    # --- Удалить: запись должна реально исчезнуть из хранилища ------------
    before = sorted(e["id"] for e in groups.load())
    parent, sub = _entry_item_with(menu, DELETE_GLYPH)
    ICON_CALLS[:] = []
    _click(_sub_item(sub, DELETE_GLYPH), icon)
    after = sorted(e["id"] for e in groups.load())

    assert len(after) == len(before) - 1, \
        "удаление не сработало: %r -> %r" % (before, after)
    assert "update_menu" in ICON_CALLS, "после удаления меню не обновилось"
    print("удалён пункт %r: %r -> %r (меню обновлено)"
          % (parent.text, before, after))

    # --- регрессия арности: обработчики должны быть 0-арными --------------
    for needle in ("Восстановить", DELETE_GLYPH):
        sub = _entry_item_with(tray._make_menu(icon), needle)[1]
        for item in sub.items:
            code = getattr(item._action, "__code__", None)
            if code is not None:
                assert code.co_argcount == 0, (
                    "%r: у обработчика %d параметр(ов) - pystray подставит "
                    "icon, id потеряется" % (item.text, code.co_argcount))

    # --- ПОЧЕМУ старый код не работал (демонстрация) ----------------------
    old_seen = []
    old_action = pystray.MenuItem(
        "x", (lambda i="entry-id": old_seen.append(i)))._action
    old_action(icon, None)            # так pystray зовёт обработчик
    assert old_seen and old_seen[0] is icon, (
        "демонстрация: старая форма должна получить icon вместо id, "
        "а получила %r" % (old_seen,))
    print("старая форма lambda i=eid: -> argcount=%d, pystray подставлял %s "
          "вместо id (поэтому удаление молча ничего не делало)"
          % (old_action.__code__.co_argcount, type(old_seen[0]).__name__))

    groups.clear()
    print("OK: обработчики меню трея получают корректный id, удаление работает")


if __name__ == "__main__":
    main()
  
