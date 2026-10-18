"""FRUit — хранение именованных снапшотов (JSON).

Снапшоты — это данные пользователя, они живут вне репозитория:
по умолчанию в %LOCALAPPDATA%\\FRUit\\snapshots (каталог — из FRUIT_DATA, см.
fruit.paths), либо аргументом --dir.
"""

from __future__ import annotations

import json
import os
import time
from typing import List, Optional, Tuple

from . import paths
from .core import Tab, Window
from .winapi import WindowGeometry


def data_dir() -> str:
    snaps = os.path.join(paths.data_dir(), "snapshots")
    os.makedirs(snaps, exist_ok=True)
    return snaps


def _sanitize(name: str) -> str:
    keep = "-_.() "
    cleaned = "".join(c for c in name if c.isalnum() or c in keep).strip()
    return cleaned or "snapshot"


def _window_to_dict(w: Window) -> dict:
    geo = None
    if w.geometry:
        geo = {"left": w.geometry.left, "top": w.geometry.top,
               "width": w.geometry.width, "height": w.geometry.height,
               "state": w.geometry.state}
    return {
        "active": w.active,
        "geometry": geo,
        "tabs": [
            {"path": t.path, "name": t.name, "virtual": t.virtual, "url": t.url}
            for t in w.tabs
        ],
    }


def _window_from_dict(d: dict) -> Window:
    geo = None
    g = d.get("geometry")
    if g:
        geo = WindowGeometry(g["left"], g["top"], g["width"], g["height"], g["state"])
    tabs = [
        Tab(path=t.get("path"), name=t.get("name", ""),
            virtual=t.get("virtual", False), url=t.get("url", ""))
        for t in d.get("tabs", [])
    ]
    return Window(tabs=tabs, active=int(d.get("active", 0)), geometry=geo)


def save_snapshot(name: str, windows: List[Window]) -> str:
    path = os.path.join(data_dir(), _sanitize(name) + ".json")
    payload = {
        "version": 1,
        "saved_at": time.time(),
        "windows": [_window_to_dict(w) for w in windows],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path


def load_snapshot(name: str) -> List[Window]:
    path = os.path.join(data_dir(), _sanitize(name) + ".json")
    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    return [_window_from_dict(w) for w in payload.get("windows", [])]


def snapshot_path(name: str) -> str:
    return os.path.join(data_dir(), _sanitize(name) + ".json")


def list_snapshots() -> List[Tuple[str, float, int, int]]:
    """Список снапшотов: (имя, время сохранения, окон, вкладок)."""
    out = []
    d = data_dir()
    for fn in os.listdir(d):
        if not fn.endswith(".json"):
            continue
        full = os.path.join(d, fn)
        try:
            with open(full, "r", encoding="utf-8") as f:
                payload = json.load(f)
            windows = payload.get("windows", [])
            ntabs = sum(len(w.get("tabs", [])) for w in windows)
            out.append((fn[:-5], float(payload.get("saved_at", 0)), len(windows), ntabs))
        except Exception:
            continue
    out.sort(key=lambda x: x[1], reverse=True)
    return out


def delete_snapshot(name: str) -> bool:
    path = snapshot_path(name)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False


def latest_snapshot() -> Optional[str]:
    lst = list_snapshots()
    return lst[0][0] if lst else None
