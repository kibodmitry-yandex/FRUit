"""Генерирует launcher\\fruit.ico (мультиразмер) и launcher\\fruit.png (256).

Источник — launcher\\logo.png (нарисованная вручную пиктограмма «папка с
бананом»). Если логотипа нет, icons.app_icon() сам откатится к иконке,
нарисованной Pillow кодом, и .ico всё равно соберётся.

Запускать из корня FRUit:  python launcher\\make_icon.py

Почему свой writer ICO, а не Image.save(format="ICO"): внутри Pillow каждый
кадр просто resize-ится с исходного размера, а исходник у нас 4096px —
одномоментное уменьшение до 16px даёт артефакты. Здесь каждый кадр
уменьшается пошагово (вдвое за проход, LANCZOS) — см. icons._fit.
"""
import io
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)          # F:\FRUit
sys.path.insert(0, ROOT)

from PIL import Image  # noqa: E402

from fruit.icons import app_icon, logo_path  # noqa: E402

SIZES = [16, 24, 32, 48, 64, 128, 256]


def write_ico(path: str, base: Image.Image, sizes) -> None:
    """Пишет ICO из PNG-кадров (Windows Vista+ принимает PNG в любой размер)."""
    frames = []
    for s in sizes:
        im = base if base.size == (s, s) else base.resize((s, s), Image.LANCZOS)
        buf = io.BytesIO()
        im.convert("RGBA").save(buf, format="PNG")
        frames.append(buf.getvalue())

    out = struct.pack("<HHH", 0, 1, len(frames))     # ICONDIR: reserved, type, count
    offset = 6 + 16 * len(frames)                    # после заголовков идут сами кадры
    for s, data in zip(sizes, frames):
        # в записи 0 означает 256 (поле — один байт)
        b = 0 if s >= 256 else s
        out += struct.pack("<BBBBHHII", b, b, 0, 0, 1, 32, len(data), offset)
        offset += len(data)
    out += b"".join(frames)

    with open(path, "wb") as f:
        f.write(out)


def main() -> None:
    src = logo_path()
    print("source:", src or "(нет логотипа — будет нарисованная иконка)")
    base = app_icon(256)                     # источник для всех размеров

    ico = os.path.join(HERE, "fruit.ico")
    png = os.path.join(HERE, "fruit.png")
    write_ico(ico, base, SIZES)
    base.save(png, format="PNG")
    print("written:", ico, "(кадры: %s)" % ", ".join(str(s) for s in SIZES))
    print("written:", png)


if __name__ == "__main__":
    main()
