"""Рисует превью иконки FRUit в разных размерах -> tools\\out\\preview.png.

Верхний ряд — реальные размеры, нижний — те же иконки, увеличенные в 4 раза
(чтобы разглядеть форму при малых размерах, как в трее).
Запуск:  python tools\\make_preview.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))

from PIL import Image, ImageDraw  # noqa: E402

from fruit.icons import app_icon  # noqa: E402

SIZES = [16, 24, 32, 48, 64]     # список в системе координат трея
SCALE = 4
GAP = 24
BIG = 256
CHECK = 12


def checkerboard(w, h):
    img = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    d = ImageDraw.Draw(img)
    for y in range(0, h, CHECK):
        for x in range(0, w, CHECK):
            if ((x // CHECK) + (y // CHECK)) % 2:
                d.rectangle([x, y, x + CHECK - 1, y + CHECK - 1], fill=(228, 228, 228, 255))
    return img


def main() -> None:
    os.makedirs(OUT, exist_ok=True)

    width = BIG + GAP
    for s in SIZES:
        width += s * SCALE + GAP
    row_h = max(BIG, max(s * SCALE for s in SIZES)) + GAP * 2
    height = row_h * 2 + GAP

    sheet = checkerboard(width, height)
    d = ImageDraw.Draw(sheet)

    y_actual = GAP
    y_scaled = row_h + GAP

    # 256 — реальный размер
    sheet.alpha_composite(app_icon(BIG), (GAP, y_actual))
    d.text((GAP, y_actual + BIG + 4), "256", fill=(30, 30, 30, 255))

    x = BIG + GAP * 2
    for s in SIZES:
        ic = app_icon(s)
        cw = s * SCALE
        sheet.alpha_composite(ic, (x + (cw - s) // 2, y_actual))
        d.text((x, y_actual - 14), f"{s}px", fill=(30, 30, 30, 255))
        sheet.alpha_composite(ic.resize((cw, cw), Image.NEAREST), (x, y_scaled))
        d.text((x, y_scaled + cw + 4), f"{s}px x{SCALE}", fill=(30, 30, 30, 255))
        x += cw + GAP

    out = os.path.join(OUT, "preview.png")
    sheet.save(out)
    print("written:", out, sheet.size)


if __name__ == "__main__":
    main()
