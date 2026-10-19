"""FRUit — Folder Restore Utility (for Explorer navigation).

FRU = Folder Restore Utility; «it» добавлено для читаемости (чтобы
складывалось в «fruit»).

Вызывается как ``python -m fruit <команды>`` (см. fruit.cli) либо
``python -m fruit tray`` (см. fruit.tray). Пакет импортируется при любом
запуске, поэтому здесь же готовим ``comtypes.gen`` (см. ниже).
"""

from __future__ import annotations

__version__ = "0.3.0"
__all__ = ["core", "snapshots", "groups", "winapi", "tabs", "icons", "cli", "tray"]


def _ensure_comtypes_gen() -> None:
    """Создаёт пакет ``comtypes.gen`` заранее.

    comtypes создаёт ``comtypes/gen`` сам при первом импорте, но из-за кэша
    файлового импортёра Python этот же импорт может упасть с
    ``ImportError: cannot import name 'gen' from 'comtypes'``. Готовим каталог
    и сбрасываем кэш импортёра до того, как comtypes начнёт работать.
    """
    try:
        import comtypes
    except Exception:
        return  # comtypes не установлен — не наша забота здесь
    try:
        import comtypes.gen  # noqa: F401
        return
    except Exception:
        pass
    try:
        import importlib
        import os

        gen_dir = os.path.join(comtypes.__path__[0], "gen")
        os.makedirs(gen_dir, exist_ok=True)
        init_py = os.path.join(gen_dir, "__init__.py")
        if not os.path.exists(init_py):
            with open(init_py, "w", encoding="utf-8") as f:
                f.write("# comtypes.gen package, directory for generated files.\n")
        importlib.invalidate_caches()
    except Exception:
        pass


_ensure_comtypes_gen()
