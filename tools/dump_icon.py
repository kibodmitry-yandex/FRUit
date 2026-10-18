"""Печатает иконку FRUit в виде ASCII.

B — банан, F — папка, T — вкладка, . — прозрачно.

Режимы:
  python tools\\dump_icon.py 64            # app_icon(64)
  python tools\\dump_icon.py 16 64 chain   # app_icon(64) -> 32 -> 16 (как масштабирует Windows)
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
for s in (sys.stdout, sys.stderr):
    try:
        s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from PIL import Image  # noqa: E402

from fruit import icons  # noqa: E402

ITEMS = [("B", icons._BANANA), ("B", icons._BANANA_LIGHT),
         ("B", icons._BANANA_DARK), ("B", icons._BANANA_TIP),
         ("F", icons._FOLDER), ("F", icons._FOLDER_LIGHT),
         ("F", icons._FOLDER_DARK), ("T", icons._TAB), ("T", icons._TAB_LIGHT)]


def classify(r, g, b):
    best, bd = "?", 1 << 30
    for cls, (R, G, B) in ITEMS:
        d = (r - R) ** 2 + (g - G) ** 2 + (b - B) ** 2
        if d < bd:
            bd, best = d, cls
    return best


def show(im, title):
    im = im.convert("RGBA")
    px = im.load()
    counts = {"B": 0, "F": 0, "T": 0}
    print(f"=== {title} ({im.size[0]}px) ===")
    for y in range(im.size[1]):
        row = ""
        for x in range(im.size[0]):
            r, g, b, a = px[x, y]
            if a < 40:
                row += "."
            else:
                c = classify(r, g, b)
                row += c
                counts[c] = counts.get(c, 0) + 1
        print(row)
    print("пикселей: банан=%d папка=%d вкладка=%d" % (counts["B"], counts["F"], counts["T"]))


def main() -> None:
    args = sys.argv[1:]
    dst = int(args[0]) if args else 64
    src = int(args[1]) if len(args) > 1 else None
    chain = len(args) > 2 and args[2] == "chain"

    if src is None:
        show(icons.app_icon(dst), f"app_icon({dst})")
        return

    im = icons.app_icon(src)
    label = f"app_icon({src})"
    if chain:
        mid = max(1, src // 2)
        im = im.resize((mid, mid), Image.LANCZOS)
        label += f" -> {mid}"
    im = im.resize((dst, dst), Image.LANCZOS)
    show(im, label + f" -> {dst}")


if __name__ == "__main__":
    main()
