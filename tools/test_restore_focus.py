"""Регрессия: восстановление НЕ дублирует уже открытые окна.

core.find_matching_window(current, saved_tabs) ищет уже открытое окно,
содержащее ВСЕ вкладки восстанавливаемой раскладки; если нашли —
restore_state выводит его на передний план (summary['focused']) вместо
создания дубликата и НЕ трогает его геометрию/активную вкладку.

Тест вычислительный: core.Window/core.Tab строятся руками, а в restore_state
подменяются capture_state/focus_window/launch_folder — COM не трогается.
"""

import os
import sys

sys.path.insert(0, r"F:\FRUit")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from fruit import core, winapi


def _win(*paths, **kw):
    hwnd = kw.get("hwnd", 0)
    tabs = [core.Tab(path=p, name=os.path.basename(p)) for p in paths]
    return core.Window(tabs=tabs, hwnd=hwnd)


def test_matching():
    cur = [
        _win(r"F:\A", r"F:\B", r"F:\C", hwnd=100),     # широкое окно
        _win(r"G:\X", r"G:\Y", hwnd=200),              # точное совпадение
        _win(r"F:\A", hwnd=300),                       # одиночка
    ]

    # точное совпадение набора вкладок (порядок не важен)
    m = core.find_matching_window(cur, _win(r"G:\Y", r"G:\X").tabs)
    assert m is not None and m.hwnd == 200, m

    # вкладка восстанавливаемой раскладки есть и в широком окне, и в одиночке:
    # берём самое узкое
    m = core.find_matching_window(cur, _win(r"F:\A").tabs)
    assert m is not None and m.hwnd == 300, m

    # раскладка целиком лежит внутри широкого окна — подходит и оно
    m = core.find_matching_window(cur, _win(r"F:\A", r"F:\B").tabs)
    assert m is not None and m.hwnd == 100, m

    # ничего похожего открыто нет
    assert core.find_matching_window(cur, _win(r"Z:\none").tabs) is None

    # виртуальные вкладки (This PC и т.п.) не участвуют в сравнении
    virt = core.Window(tabs=[core.Tab(path=None, name="Этот компьютер",
                                      virtual=True)])
    assert core.find_matching_window(cur, virt.tabs) is None
    print("find_matching_window: точное совпадение, самое узкое окно, "
          "полный отказ — OK")


def _patch(fake_current, focused, opened):
    """Подменяет COM-границы core: съём, фокус, открытие."""
    core.capture_state = lambda: list(fake_current)
    winapi.focus_window = lambda hwnd: (focused.append(hwnd) or True)
    winapi.launch_folder = lambda path: (opened.append(path) or True)
    core._find_window_hwnd_by_path = lambda *a, **kw: None


def test_restore_focuses_instead_of_duplicating():
    fake = [_win(r"F:\A", hwnd=4242)]
    focused, opened = [], []
    _patch(fake, focused, opened)

    summary = core.restore_state([_win(r"F:\A")])
    assert summary["focused"] == 1, summary
    assert summary["opened"] == 0 and summary["tabs"] == 0, summary
    assert focused == [4242], focused
    assert opened == [], "уже открытое окно не должно пересоздаваться: %r" % (opened,)
    print("restore_state: открытое окно выведено на передний план, "
          "дубликат не создан (summary=%r)" % summary)


def test_restore_opens_when_nothing_matches():
    focused, opened = [], []
    _patch([], focused, opened)

    summary = core.restore_state([_win(r"F:\A", r"F:\B")])
    assert focused == [], focused
    # группировка не удалась (окно не нашлось) — обе папки открыты отдельными
    assert summary["opened"] == 2, summary
    assert opened == [r"F:\A", r"F:\B"], opened
    print("restore_state: без совпадений раскладка открывается как раньше "
          "(summary=%r)" % summary)


if __name__ == "__main__":
    test_matching()
    test_restore_focuses_instead_of_duplicating()
    test_restore_opens_when_nothing_matches()
    print("OK: восстановление не дублирует открытые окна")
