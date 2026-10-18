"""Генерирует launcher\\fruit.ico (мультиразмер) и launcher\\fruit.png (256).

Иконка рисуется Pillow кодом из fruit\\icons.py — бинарных ассетов в репозитории
нет. Запускать из корня FRUit:  python launcher\\make_icon.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)          # F:\FRUit
sys.path.insert(0, ROOT)

from PIL import Image  # noqa: E402
from fruit.icons import app_icon  # noqa: E402

SIZES = [16, 24, 32, 48, 64, 128, 256]


def main() -> None:
    big = app_icon(256)                       # источник для всех размеров
    ico = os.path.join(HERE, "fruit.ico")
    png = os.path.join(HERE, "fruit.png")
    big.save(ico, format="ICO", sizes=[(s, s) for s in SIZES])
    big.save(png, format="PNG")
    print("written:", ico)
    print("written:", png)


if __name__ == "__main__":
    main()
