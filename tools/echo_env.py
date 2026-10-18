"""Печатает FRUIT_DATA/FRUIT_HOME — проверка изоляции данных в скриптах."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
for s in (sys.stdout, sys.stderr):
    try:
        s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from fruit import paths  # noqa: E402

print("FRUIT_DATA env :", os.environ.get("FRUIT_DATA"))
print("FRUIT_HOME env :", os.environ.get("FRUIT_HOME"))
print("data_dir()     :", paths.data_dir())
