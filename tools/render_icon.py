"""Рендер иконки FRUit в контактный лист для визуальной проверки.

Кладёт tools/out/icon_preview.png: иконка в размерах 16..128 на светлом и
тёмном фоне (трей бывает на любом).
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PIL import Image  # noqa: E402

from fruit.icons import app_icon  # noqa: E402

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "out", "icon_preview.png"))

sizes = [16, 24, 32, 48, 64, 128]
pad = 14
big = max(sizes)

light = (238, 238, 242, 255)
dark = (30, 32, 38, 255)

w = sum(s + pad for s in sizes) + pad
h = big + 2 * pad
sheet = Image.new("RGBA", (w, h * 2), (0, 0, 0, 0))

x = pad
for s in sizes:
    ic = app_icon(s)
    y = (big - s) // 2
    sheet.alpha_composite(ic, (x, pad + y))
    sheet.alpha_composite(ic, (x, h + pad + y))
    x += s + pad

bg = Image.new("RGBA", (w, h * 2))
bg.paste(light, (0, 0, w, h))
bg.paste(dark, (0, h, w, h))
out = Image.alpha_composite(bg, sheet)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
out.save(OUT)
app_icon(256).save(os.path.join(os.path.dirname(OUT), "icon_256.png"))
print(OUT)
print(os.path.join(os.path.dirname(OUT), "icon_preview.png"))
