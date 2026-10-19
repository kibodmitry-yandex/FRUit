"""Печатает контекстное меню трея текстом — удобно смотреть, что выйдет,
не открывая трей (в т.ч. новый состав групп в подменю).

По умолчанию читает РЕАЛЬНЫЙ список (``%LOCALAPPDATA%\\FRUit`), ТОЛЬКО ДЛЯ
ЧТЕНИЯ: ничего не пишет и не чистит. Можно указать свой каталог данных:

    python tools\\dump_menu.py             :: реальный список
    python tools\\dump_menu.py <каталог>   :: свой каталог (FRUIT_DATA)
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if len(sys.argv) > 1:
    os.environ["FRUIT_DATA"] = sys.argv[1]

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import pystray

from fruit import groups, tray


class _Icon(object):
    """Заглушка значка: _menu_items() трогает icon только в пункте «Выход»."""

    def stop(self):
        pass


def dump(menu, prefix=""):
    """Печатает пункты меню и их подменю с отступами."""
    for item in menu.items:
        if item is pystray.Menu.SEPARATOR or item.text.startswith("- - -"):
            print(prefix + "─" * 24)
            continue
        note = "" if item.enabled else "   (только чтение)"
        print(prefix + item.text + note)
        if item.submenu is not None:
            dump(item.submenu, prefix + "    ")


def main():
    print("файл списка: %s" % groups.store_path())
    print("запомнено раскладок: %d" % len(groups.load()))
    print()
    print("меню трея (правый клик):")
    dump(tray._make_menu(_Icon()))


if __name__ == "__main__":
    main()
  
