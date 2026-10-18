"""FRUit — где живут пользовательские данные (вне репозитория).

По умолчанию ``%LOCALAPPDATA%\\FRUit``. Переопределяется переменной окружения
``FRUIT_DATA``.

Не путать с ``FRUIT_HOME``: её использует exe-лаунчер как каталог с пакетом
``fruit`` (где лежит код). Данные и код разделены намеренно.
"""

from __future__ import annotations

import os


def data_dir() -> str:
    """Каталог данных FRUit (создаётся при обращении)."""
    base = os.environ.get("FRUIT_DATA")
    if not base:
        base = os.path.join(
            os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "FRUit"
        )
    os.makedirs(base, exist_ok=True)
    return base
