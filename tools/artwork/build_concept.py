"""生成概念图里的两个新素材：页脚天际线剪影、列宁头像剪影。

输出到 soviet_theme/out/ 与源码树 assets/images/soviet/：
  skyline.png        1600x420，深红剪影，透明背景（工厂/烟囱/厂房/远山/旗帜）
  header_lenin.png   420x520，米白剪影（从列宁照片阈值化），透明背景
"""
from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps

WORK = Path(__file__).resolve().parent
SRC = WORK / 'src_assets'
OUT = WORK / 'out'
TREE = Path(r'D:\Jordan5K-Mod-Tools-RePack\Jordan5k-Mod-Tools-RePack\Mod Tools\BepInEx\_work\flclash\FlClash-0.9.2\assets\images\soviet')

RED_DEEP = (94, 12, 14, 255)
RED_MID = (140, 22, 24, 255)
CREAM = (247, 236, 216, 255)


def skyline(width: int = 1600, height: int = 420) -> Image.Image:
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    ground = height - 8

    # 远山（半透明，做出层叠纵深）
    hill = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hill)
    hd.polygon(
        [(0, ground), (0, 300), (240, 176), (430, 268), (640, 208),
         (880, 292), (1080, 226), (1300, 300), (1600, 240), (1600, ground)],
        fill=(146, 30, 26, 90),
    )
    img.alpha_composite(hill)

    # 天际线：厂房 + 烟囱 + 塔吊 + 水塔
    rng = random.Random(5)
    x = -20
    while x < width:
        kind = rng.choice(['block', 'saw', 'tower', 'chimney', 'block'])
        if kind == 'block':
            w = rng.randint(70, 150)
            h = rng.randint(70, 150)
            draw.rectangle([x, ground - h, x + w, ground], fill=RED_DEEP)
            for wy in range(ground - h + 16, ground - 24, 30):
                for wx in range(x + 14, x + w - 18, 26):
                    draw.rectangle([wx, wy, wx + 9, wy + 13], fill=RED_MID)
            x += w + rng.randint(6, 22)
        elif kind == 'saw':
            w = rng.randint(120, 200)
            h = rng.randint(60, 100)
            draw.rectangle([x, ground - h, x + w, ground], fill=RED_DEEP)
            teeth = 6
            step = w / teeth
            for i in range(teeth):
                draw.polygon(
                    [(x + i * step, ground - h), (x + (i + 1) * step, ground - h),
                     (x + (i + 0.5) * step, ground - h - 26)],
                    fill=RED_DEEP,
                )
            x += w + rng.randint(10, 26)
        elif kind == 'chimney':
            w = rng.randint(26, 40)
            h = rng.randint(200, 300)
            draw.rectangle([x, ground - h, x + w, ground], fill=RED_DEEP)
            draw.rectangle([x - 5, ground - h - 10, x + w + 5, ground - h], fill=RED_DEEP)
            smoke = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            sd = ImageDraw.Draw(smoke)
            sd.ellipse([x - 30, ground - h - 60, x + w + 30, ground - h - 10],
                       fill=(150, 34, 30, 110))
            smoke = smoke.filter(ImageFilter.GaussianBlur(9))
            img.alpha_composite(smoke)
            x += w + rng.randint(24, 60)
        elif kind == 'tower':
            w = rng.randint(90, 120)
            h = rng.randint(120, 170)
            draw.rectangle([x, ground - h, x + w, ground], fill=RED_DEEP)
            draw.line([(x + w * 0.5, ground - h - 120), (x + w * 0.5, ground - h)],
                      fill=RED_DEEP, width=7)
            draw.line([(x + w * 0.5 - 60, ground - h - 84), (x + w * 0.5 + 60, ground - h - 84)],
                      fill=RED_DEEP, width=6)
            draw.line([(x + w * 0.5, ground - h - 120), (x + w * 0.5 - 60, ground - h - 84)],
                      fill=RED_DEEP, width=5)
            draw.line([(x + w * 0.5, ground - h - 120), (x + w * 0.5 + 60, ground - h - 84)],
                      fill=RED_DEEP, width=5)
            x += w + rng.randint(14, 34)

    # 地面
    draw.rectangle([0, ground, width, height], fill=RED_DEEP)
    # 右下的红旗（大三角）
    draw.polygon([(width - 520, height), (width, height - 300), (width, height)],
                 fill=RED_MID)
    return img


def lenin_silhouette() -> Image.Image:
    src = Image.open(SRC / 'lenin_1920.jpg').convert('L')
    src = ImageOps.autocontrast(src)
    # 阈值化成剪影：暗部保留（人像），亮部透明
    mask = src.point(lambda v: 0 if v > 96 else 255)
    mask = mask.filter(ImageFilter.GaussianBlur(1.6))
    canvas = Image.new('RGBA', src.size, CREAM)
    canvas.putalpha(mask)
    # 裁掉下方过长的西装部分，保留头肩
    w, h = canvas.size
    canvas = canvas.crop((int(w * 0.05), 0, int(w * 0.98), int(h * 0.72)))
    canvas = canvas.resize((420, int(420 * canvas.height / canvas.width)), Image.LANCZOS)
    return canvas


def main() -> int:
    OUT.mkdir(exist_ok=True)
    TREE.mkdir(parents=True, exist_ok=True)
    sky = skyline()
    sky.save(OUT / 'skyline.png')
    sky.save(TREE / 'skyline.png')
    portrait = lenin_silhouette()
    portrait.save(OUT / 'header_lenin.png')
    portrait.save(TREE / 'header_lenin.png')
    print(f'skyline {sky.size} header_lenin {portrait.size}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
