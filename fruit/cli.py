"""FRUit — командная строка.

Команды:
  fruit save <имя>          сохранить текущие окна/вкладки
  fruit list                список снапшотов
  fruit restore <имя>       восстановить снапшот (или 'latest')
  fruit delete <имя>        удалить снапшот

Флаг restore:
  --no-tabs                 не группировать вкладки (каждая папка отдельным окном)
"""

from __future__ import annotations

import argparse
import datetime
import sys
from typing import List, Optional

from . import core, snapshots


def _cmd_save(args) -> int:
    windows = core.capture_state()
    ntabs = sum(len(w.tabs) for w in windows)
    path = snapshots.save_snapshot(args.name, windows)
    print(f"Сохранено «{args.name}»: окон {len(windows)}, вкладок {ntabs}")
    print(f"Файл: {path}")
    return 0


def _cmd_list(_args) -> int:
    snaps = snapshots.list_snapshots()
    if not snaps:
        print("Снапшотов нет. Создайте: fruit save <имя>")
        return 0
    print(f"{'ИМЯ':24} {'ДАТА':17} ОКОН  ВКЛАДОК")
    for name, ts, nwin, ntabs in snaps:
        dt = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
        print(f"{name:24} {dt:17} {nwin:4}  {ntabs:7}")
    return 0


def _resolve_name(name: str) -> Optional[str]:
    if name == "latest":
        return snapshots.latest_snapshot()
    return name


def _cmd_restore(args) -> int:
    name = _resolve_name(args.name)
    if not name:
        print("Нет снапшотов для восстановления.")
        return 1
    try:
        windows = snapshots.load_snapshot(name)
    except FileNotFoundError:
        print(f"Снапшот «{name}» не найден. Список: fruit list")
        return 1
    if not windows:
        print(f"Снапшот «{name}» пуст.")
        return 1
    summary = core.restore_state(windows, group_tabs=not args.no_tabs)
    print(
        f"Восстановлено «{name}»: открыто окон {summary['opened']}, "
        f"сгруппировано вкладок {summary['tabs']}, откатов на окна {summary['fallback']}"
    )
    return 0


def _cmd_delete(args) -> int:
    name = _resolve_name(args.name)
    if name and snapshots.delete_snapshot(name):
        print(f"Удалён снапшот «{name}»")
        return 0
    print(f"Снапшот «{args.name}» не найден.")
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fruit",
        description="FRUit — сохранение и восстановление окон и вкладок Проводника Windows 11",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_save = sub.add_parser("save", help="сохранить текущие окна/вкладки")
    p_save.add_argument("name", help="имя снапшота")
    p_save.set_defaults(func=_cmd_save)

    p_list = sub.add_parser("list", help="список снапшотов")
    p_list.set_defaults(func=_cmd_list)

    p_restore = sub.add_parser("restore", help="восстановить снапшот")
    p_restore.add_argument("name", help="имя снапшота или 'latest'")
    p_restore.add_argument("--no-tabs", action="store_true",
                           help="не группировать вкладки (отдельные окна)")
    p_restore.set_defaults(func=_cmd_restore)

    p_delete = sub.add_parser("delete", help="удалить снапшот")
    p_delete.add_argument("name", help="имя снапшота или 'latest'")
    p_delete.set_defaults(func=_cmd_delete)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    # корректный русский вывод в консоли Windows (legacy codepage -> UTF-8)
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
