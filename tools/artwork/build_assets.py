# -*- coding: utf-8 -*-
"""生成 FlClash 苏联主题所需的全套栅格素材。

用法：python build_assets.py
输出：soviet_theme/out/  （随后由 install_*.ps1 / apply_runtime_theme.py 分发）
"""
from __future__ import annotations

import math
import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'src_assets')
OUT = os.path.join(HERE, 'out')
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- 苏联调色板
RED = (193, 18, 31)          # #C1121F 旗帜红
RED_DEEP = (110, 10, 17)     # #6E0A11
RED_BRIGHT = (230, 57, 70)   # #E63946
BLOOD = (127, 13, 19)        # #7F0D13
GOLD = (232, 178, 28)        # #E8B21C
GOLD_PALE = (247, 214, 122)  # #F7D67A
INK = (18, 16, 15)           # #12100F
PAPER = (237, 227, 208)      # #EDE3D0
STEEL = (138, 143, 153)      # #8A8F99
AMBER = (241, 132, 11)       # #F1840B

SS = 4  # 超采样倍率


def star_points(cx: float, cy: float, r_out: float, r_in: float,
                rotation: float = -math.pi / 2) -> list[tuple[float, float]]:
    pts = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        a = rotation + i * math.pi / 5
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def star_layer(size: int, color, rot: float = -math.pi / 2, inner: float = 0.382,
               scale: float = 1.0) -> Image.Image:
    """返回 size×size 的纯色五角星 RGBA 图层（抗锯齿）。"""
    big = size * SS
    im = Image.new('RGBA', (big, big), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = big / 2
    r_out = c * 0.98 * scale
    d.polygon(star_points(c, c, r_out, r_out * inner, rot), fill=color)
    return im.resize((size, size), Image.LANCZOS)


def gold_glyph_mask(size: int) -> Image.Image:
    """从维基的「锤子镰刀」图里抠出金色字形，输出 size×size 的 L 蒙版。"""
    src = Image.open(os.path.join(SRC, 'hammer_sickle.png')).convert('RGB')
    px = src.load()
    w, h = src.size
    mask = Image.new('L', (w, h), 0)
    mp = mask.load()
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            if r > 170 and g > 130 and b < 130:
                mp[x, y] = 255
    box = mask.getbbox()
    mask = mask.crop(box)
    mask = mask.resize((size, size), Image.LANCZOS)
    return mask


def glyph_layer(size: int, color) -> Image.Image:
    mask = gold_glyph_mask(size)
    layer = Image.new('RGBA', (size, size), color)
    layer.putalpha(mask)
    return layer


def vgradient(size: tuple[int, int], top, bottom) -> Image.Image:
    w, h = size
    im = Image.new('RGB', (w, 1))
    for x in range(w):
        im.putpixel((x, 0), top)
    grad = Image.new('RGB', (w, h))
    for y in range(h):
        t = y / max(h - 1, 1)
        row = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        grad.paste(row, (0, y, w, y + 1))
    return grad


def rounded_mask(size: int, radius: int) -> Image.Image:
    m = Image.new('L', (size, size), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size - 1, size - 1],
                                        radius=radius, fill=255)
    return m


# ------------------------------------------------------------------- 应用图标
def build_icon(size: int = 512) -> Image.Image:
    base = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    grad = vgradient((size, size), RED, RED_DEEP).convert('RGBA')

    # 建构主义斜光束
    rays = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rays)
    for k in range(-2, 9):
        x = k * size / 6
        rd.polygon([(x, size), (x + size * 0.16, size),
                    (x + size * 0.62, 0), (x + size * 0.46, 0)],
                   fill=(255, 255, 255, 16))
    grad.alpha_composite(rays)

    base.alpha_composite(grad)
    base.putalpha(rounded_mask(size, int(size * 0.19)))

    # 金色描边
    border = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(border).rounded_rectangle(
        [int(size * 0.021), int(size * 0.021),
         size - int(size * 0.021), size - int(size * 0.021)],
        radius=int(size * 0.172), outline=GOLD + (235,),
        width=max(2, int(size * 0.011)))
    base.alpha_composite(border)

    # 金色五角星，星内镂空锤子镰刀（透出底层旗帜红）
    star = star_layer(size, GOLD + (255,), inner=0.42, scale=0.74)
    outer = int(size * 0.74) + 2
    halo = star_layer(size, RED_DEEP + (255,), inner=0.42, scale=0.762)
    base.alpha_composite(halo)

    glyph_size = int(size * 0.375)
    hole = Image.new('L', (size, size), 0)
    hole.paste(gold_glyph_mask(glyph_size),
               ((size - glyph_size) // 2, int(size * 0.245)))
    star.putalpha(ImageChops.subtract(star.split()[3], hole))
    base.alpha_composite(star)
    return base


def build_star_icon(size: int, color, rim=None) -> Image.Image:
    im = star_layer(size, color + (255,), inner=0.40, scale=0.92)
    if rim:
        rim_layer = star_layer(size, rim + (255,), inner=0.40, scale=1.0)
        rim_layer.alpha_composite(im)
        im = rim_layer
    return im


# ------------------------------------------------------------------ 托盘图标
def build_tray(color, badge=None) -> Image.Image:
    size = 64
    im = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    star = build_star_icon(size, color, rim=(20, 16, 14))
    im.alpha_composite(star)
    return im


# -------------------------------------------------------------------- 头像
def duotone(im: Image.Image, dark, light) -> Image.Image:
    g = im.convert('L')
    return Image.merge('RGB', (
        g.point(lambda v, d=dark[0], l=light[0]: int(d + (l - d) * v / 255)),
        g.point(lambda v, d=dark[1], l=light[1]: int(d + (l - d) * v / 255)),
        g.point(lambda v, d=dark[2], l=light[2]: int(d + (l - d) * v / 255)),
    ))


def cover(im: Image.Image, size: tuple[int, int]) -> Image.Image:
    tw, th = size
    w, h = im.size
    scale = max(tw / w, th / h)
    im = im.resize((max(tw, int(w * scale + 0.5)), max(th, int(h * scale + 0.5))),
                   Image.LANCZOS)
    w, h = im.size
    left = (w - tw) // 2
    top = int((h - th) * 0.42)
    return im.crop((left, top, left + tw, top + th))


def build_avatars() -> None:
    lenin = Image.open(os.path.join(SRC, 'lenin_1920.jpg'))
    stalin = Image.open(os.path.join(SRC, 'stalin_official.jpg'))

    a = duotone(cover(lenin, (960, 1280)), (26, 12, 10), (255, 226, 190))
    a.save(os.path.join(OUT, 'avatar_arue.jpg'), quality=88, optimize=True)

    b = duotone(cover(stalin, (640, 640)), (20, 8, 8), (255, 214, 168))
    b.save(os.path.join(OUT, 'avatar_june2.jpg'), quality=88, optimize=True)


# -------------------------------------------------------------- 宣传画素材
def load_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    for name in (('PT_SansNarrow-Bold.ttf', 'PT_SansNarrow-Regular.ttf') if bold
                 else ('PT_SansNarrow-Regular.ttf',)):
        p = os.path.join(SRC, name)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', size)


def build_poster(photo_path: str, title: str, out_name: str,
                 size=(680, 900)) -> None:
    w, h = size
    im = duotone(cover(Image.open(photo_path), (w, h)), (32, 6, 8), (255, 214, 170))
    canvas = Image.new('RGB', (w, h), BLOOD)
    canvas.paste(im, (0, 0))
    d = ImageDraw.Draw(canvas, 'RGBA')

    # 顶部红色三角
    d.polygon([(0, 0), (w, 0), (w, int(h * 0.10)), (0, int(h * 0.03))], fill=RED)
    # 金色边框
    d.rectangle([0, 0, w - 1, h - 1], outline=GOLD, width=6)
    d.rectangle([14, 14, w - 15, h - 15], outline=(232, 178, 28, 110), width=2)

    # 底部横幅
    band = int(h * 0.155)
    d.rectangle([0, h - band, w, h], fill=(122, 10, 16))
    d.line([(0, h - band), (w, h - band)], fill=GOLD, width=3)

    star = build_star_icon(72, GOLD)
    canvas.paste(star, (int(w * 0.06), h - band + (band - 72) // 2), star)

    font = load_font(int(band * 0.52))
    tw = d.textlength(title, font=font)
    d.text(((w - tw) / 2 + 30, h - band + band * 0.20), title,
           font=font, fill=PAPER)
    canvas.save(os.path.join(OUT, out_name), quality=90, optimize=True)


def build_banner(size=(1000, 128)) -> None:
    w, h = size
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im, 'RGBA')
    d.polygon([(0, int(h * 0.20)), (w, int(h * 0.06)), (w, int(h * 0.80)),
               (0, int(h * 0.94))], fill=RED + (255,))
    d.line([(0, int(h * 0.20)), (w, int(h * 0.06))], fill=GOLD + (255,), width=3)
    d.line([(0, int(h * 0.94)), (w, int(h * 0.80))], fill=GOLD + (255,), width=3)
    text = 'СЛАВА ТРУДУ · ПРОЛЕТАРИИ ВСЕХ СТРАН, СОЕДИНЯЙТЕСЬ!'
    font_size = int(h * 0.42)
    font = load_font(font_size)
    while d.textlength(text, font=font) > w * 0.86 and font_size > 12:
        font_size -= 2
        font = load_font(font_size)
    tw = d.textlength(text, font=font)
    d.text(((w - tw) / 2, int(h * 0.30)), text, font=font, fill=GOLD_PALE + (255,))
    im.save(os.path.join(OUT, 'banner.png'))


def build_flag() -> None:
    src = Image.open(os.path.join(SRC, 'ussr_flag.png')).convert('RGB')
    src = src.resize((1200, 600), Image.LANCZOS)
    src.save(os.path.join(OUT, 'flag.png'), optimize=True)


def main() -> None:
    icon = build_icon(512)
    icon.save(os.path.join(OUT, 'icon.png'), optimize=True)

    icon_ico = build_icon(256)
    icon_ico.save(os.path.join(OUT, 'icon.ico'),
                  sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64),
                         (128, 128), (256, 256)])

    for idx, color in enumerate((STEEL, RED_BRIGHT, GOLD, AMBER), start=1):
        build_tray(color).save(os.path.join(OUT, f'tray_status_{idx}.ico'),
                               sizes=[(16, 16), (20, 20), (24, 24), (32, 32),
                                      (40, 40), (48, 48), (64, 64)])

    build_avatars()
    build_flag()
    build_banner()
    build_poster(os.path.join(SRC, 'lenin_1920.jpg'), 'ЛЕНИН', 'poster_lenin.jpg')
    build_poster(os.path.join(SRC, 'stalin_official.jpg'), 'СТАЛИН',
                 'poster_stalin.jpg')

    star = build_star_icon(512, GOLD)
    star.save(os.path.join(OUT, 'star.png'), optimize=True)

    emblem = glyph_layer(1024, GOLD + (255,))
    emblem.save(os.path.join(OUT, 'emblem.png'), optimize=True)

    glyph_layer(512, INK + (255,)).save(os.path.join(OUT, 'emblem_ink.png'),
                                        optimize=True)
    print('assets written to', OUT)


if __name__ == '__main__':
    main()
