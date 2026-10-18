"""FRUit — накапливающийся список запомненных групп вкладок и окон.

Отличие от именованных снапшотов (snapshots.py): здесь ОДИН плоский список,
который пополняется действием «Сделать снапшот». Повторное запоминание
идентичной раскладки НЕ создаёт дубликата: полный дубль группы или окна
(совпадает набор путей всех вкладок) пропускается.

Запись списка = одно окно Проводника:
  * kind = "group"  — окно с несколькими вкладками (показывается по первой
    вкладке, маркер-глиф «группа»);
  * kind = "window" — окно с одной папкой (маркер-глиф «отдельное окно»).

Хранение: %LOCALAPPDATA%\\FRUit\\groups.json (каталог — из FRUIT_DATA, см.
fruit.paths).
"""

from __future__ import annotations

import json
import os
import time
import uuid
from typing import List, Optional, Tuple

from . import paths
from .core import Tab, Window
from .winapi import WindowGeometry


def store_path() -> str:
    return os.path.join(paths.data_dir(), "groups.json")


def _dedup_key(tabs: List[Tab]) -> Tuple[str, ...]:
    """Порядконезависимый ключ набора путей вкладок (для поиска полных дублей)."""
    paths = []
    for t in tabs:
        p = (t.path or t.url or t.name or "").replace("/", "\\").lower().rstrip("\\")
        paths.append(p)
    return tuple(sorted(paths))


def _entry_kind(tabs: List[Tab]) -> str:
    return "group" if len(tabs) > 1 else "window"


def _entry_label(tabs: List[Tab]) -> str:
    if tabs:
        return tabs[0].name or (tabs[0].path or "без имени")
    return "без имени"


def _window_to_entry(w: Window) -> dict:
    geo = None
    if w.geometry:
        geo = {"left": w.geometry.left, "top": w.geometry.top,
               "width": w.geometry.width, "height": w.geometry.height,
               "state": w.geometry.state}
    return {
        "id": uuid.uuid4().hex[:12],
        "kind": _entry_kind(w.tabs),
        "label": _entry_label(w.tabs),
        "created": time.time(),
        "active": w.active,
        "geometry": geo,
        "tabs": [
            {"path": t.path, "name": t.name, "virtual": t.virtual, "url": t.url}
            for t in w.tabs
        ],
    }


def _entry_to_window(e: dict) -> Window:
    geo = None
    g = e.get("geometry")
    if g:
        geo = WindowGeometry(g["left"], g["top"], g["width"], g["height"], g["state"])
    tabs = [
        Tab(path=t.get("path"), name=t.get("name", ""),
            virtual=t.get("virtual", False), url=t.get("url", ""))
        for t in e.get("tabs", [])
    ]
    return Window(tabs=tabs, active=int(e.get("active", 0)), geometry=geo)


def load() -> List[dict]:
    path = store_path()
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return list(data.get("entries", []))
    except Exception:
        return []


def _save(entries: List[dict]) -> None:
    path = store_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"version": 1, "entries": entries}, f, ensure_ascii=False, indent=2)


def add_state(windows: List[Window]) -> Tuple[int, int]:
    """Добавляет окна в список, пропуская полные дубли.

    Возвращает (добавлено, пропущено-дублей).
    """
    entries = load()
    known = {_dedup_key_from_entry(e) for e in entries}
    added = skipped = 0
    for w in windows:
        if not w.tabs:
            continue
        key = _dedup_key(w.tabs)
        if key in known:
            skipped += 1
            continue
        entries.append(_window_to_entry(w))
        known.add(key)
        added += 1
    if added:
        _save(entries)
    return added, skipped


def _dedup_key_from_entry(e: dict) -> Tuple[str, ...]:
    paths = []
    for t in e.get("tabs", []):
        p = (t.get("path") or t.get("url") or t.get("name") or "")
        p = p.replace("/", "\\").lower().rstrip("\\")
        paths.append(p)
    return tuple(sorted(paths))


def remove(entry_id: str) -> bool:
    entries = load()
    keep = [e for e in entries if e.get("id") != entry_id]
    if len(keep) == len(entries):
        return False
    _save(keep)
    return True


def clear() -> None:
    _save([])


def all_windows() -> List[Window]:
    """Все записи как окна (для «Восстановить все»)."""
    return [_entry_to_window(e) for e in load()]


def entry_window(entry_id: str) -> Optional[Window]:
    for e in load():
        if e.get("id") == entry_id:
            return _entry_to_window(e)
    return None
