"""FRUit — иконки, рисуемые Pillow (без бинарных ассетов в репозитории).

  * app_icon(size)     — главная иконка: папка (со стеком), а сверху — банан
                         (значок в трее и у exe).
  * GROUP_GLYPH / WINDOW_GLYPH / DELETE_GLYPH — символы пунктов меню.

Почему глифы, а не иконки у пунктов меню: Win32-бэкенд pystray не умеет
рисовать картинки у элементов контекстного меню. Поэтому «группа/окно»
передаётся символом в тексте пункта.

Ключевое требование — иконка должна читаться в размере трея (16 px). Поэтому:
  * банан — отдельный от папки элемент (висит над ней, в основном на прозрачном
    фоне), а не «пятно» на папке;
  * у банана тёмный контур и тёмные кончики — даже если цвета сливаются при
    уменьшении, силуэт остаётся читаемым;
  * банан ярче папки, папка — заметно оранжевее.
"""

from __future__ import annotations

from PIL import Image, ImageDraw

# Папка — насыщенный тёмно-оранжевый (чтобы банан отличался по яркости)
_FOLDER = (226, 132, 16)
_FOLDER_LIGHT = (255, 186, 74)
_FOLDER_DARK = (168, 92, 8)
_TAB = (110, 160, 230)
_TAB_LIGHT = (150, 195, 245)

# Банан — очень светлый лимонный (высокая яркость), с тёмным контуром
_BANANA = (255, 238, 110)
_BANANA_LIGHT = (255, 253, 208)
_BANANA_DARK = (118, 82, 8)
_BANANA_TIP = (84, 56, 10)


def _banana(d: ImageDraw.ImageDraw, u: float, cx: float, cy: float,
            w: float, h_out: float, h_in: float) -> None:
    """Рисует банан-полумесяц в базовых (64px) координатах, масштабируя на ``u``.

    Кончики — на уровне ``cy``, тело провисает вниз до ``cy + h_out``. Разница
    ``h_out - h_in`` задаёт толщину в середине; к кончикам она сходит на нет —
    получается «лодочка»/полумесяц, читаемый даже в 16 px.
    """
    n = 72
    outer, inner, hl = [], [], []
    for i in range(n + 1):
        t = i / n
        x = -w / 2 + w * t
        bump = 4 * t * (1 - t)          # 0 на кончиках, 1 в середине
        outer.append((x, h_out * bump))                 # нижняя дуга
        inner.append((x, h_in * bump))                  # верхняя дуга (площе)
        hl.append((x, (h_in + 0.35 * (h_out - h_in)) * bump))

    poly = inner + outer[::-1]          # обходим по периметру без самопересечений
    d.polygon([((cx + x) * u, (cy + y) * u) for x, y in poly],
              fill=_BANANA, outline=_BANANA_DARK, width=max(1, round(u)))

    d.line([((cx + x) * u, (cy + y) * u) for x, y in hl],
           fill=_BANANA_LIGHT, width=max(1, int(1.2 * u)), joint="curve")

    for ex in (-w / 2, w / 2):   # тёмные кончики
        d.ellipse([(cx + ex - 1.7) * u, (cy - 1.7) * u,
                   (cx + ex + 1.7) * u, (cy + 1.7) * u], fill=_BANANA_TIP)

    # черешок над правым кончиком
    d.line([((cx + w / 2) * u, (cy - 0.6) * u),
            ((cx + w / 2 + 1.3) * u, (cy - 4.6) * u)],
           fill=_BANANA_TIP, width=max(1, int(1.5 * u)))


def app_icon(size: int = 64) -> Image.Image:
    """Иконка FRUit: стопка папок, а над ней — банан."""
    s = size
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    u = s / 64.0  # коэффициент масштаба от базового 64px

    def rr(box, r, fill):
        d.rounded_rectangle([v * u for v in box], radius=max(0.6, r * u), fill=fill)

    # задняя папка (намёк на стопку)
    rr([12, 34, 54, 48], 3, _FOLDER_DARK)
    # вкладка задней папки
    rr([18, 38, 48, 41], 2, _TAB)
    # передняя папка с язычком
    rr([8, 42, 56, 58], 4, _FOLDER)
    rr([8, 36, 28, 46], 3, _FOLDER)
    # блик
    rr([12, 48, 52, 51], 2, _FOLDER_LIGHT)

    # банан «парит» НАД папкой (без наложения): кончики вверх, тело провисает
    _banana(d, u, cx=32, cy=9, w=48, h_out=25, h_in=8.0)

    return img


def tray_icon(size: int = 64) -> Image.Image:
    """То же, что app_icon — отдельное имя для ясности."""
    return app_icon(size)


# --- глифы для пунктов меню (текст, а не картинки) -------------------------
GROUP_GLYPH = "\U0001F5C2"      # 🗂 — картотека (несколько вкладок)
WINDOW_GLYPH = "\U0001F5C0"     # 🗀 — папка (одно окно)
DELETE_GLYPH = "\u2716"         # ✕ — крестик удаления
