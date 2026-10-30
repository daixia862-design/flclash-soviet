"""画一张主题效果图：用源码里定好的苏联配色，照 FlClash 的版式做一张样张。

不上机编译 Flutter 也能看到改动后的样子：深色版（默认）与浅色版（做旧纸张）。
生成 preview_dark.png、preview_light.png、preview.png（上下拼合）。
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / 'out'
FONTS = HERE / 'src_assets'
CJK = Path(r'C:\Windows\Fonts\msyh.ttc')

W, H = 1120, 720
M = 24

DARK = {
    'window': '#120B0B',
    'sidebar': '#1B1111',
    'card': '#1B1111',
    'card_alt': '#241717',
    'outline': '#3E2C24',
    'text': '#F2E7D8',
    'text_dim': '#C4B6A4',
    'primary': '#F0434E',
    'on_primary': '#2A0609',
    'gold': '#E8B21C',
    'gold_pale': '#F7D67A',
    'paper': '#EDE3D0',
    'steel': '#A9B2BF',
    'ok': '#E8B21C',
}

LIGHT = {
    'window': '#EDE3D0',
    'sidebar': '#F1E7D4',
    'card': '#F7EFE0',
    'card_alt': '#E8DBC6',
    'outline': '#CFC0A8',
    'text': '#14100F',
    'text_dim': '#514537',
    'primary': '#A50F1B',
    'on_primary': '#FFF8E7',
    'gold': '#8A5A00',
    'gold_pale': '#B98A00',
    'paper': '#FFFCF4',
    'steel': '#4C5561',
    'ok': '#8A5A00',
}

NAV = ['ПРОКСИ', 'ПРОФИЛИ', 'ПРАВИЛА', 'ЖУРНАЛ', 'НАСТРОЙКИ']
NODES = [
    ('МОСКВА · 01', '32 мс', True),
    ('ЛЕНИНГРАД · 02', '48 мс', True),
    ('КИЕВ · 03', '87 мс', False),
    ('ВЛАДИВОСТОК · 04', '142 мс', False),
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = 'PT_SansNarrow-Bold.ttf' if bold else 'PT_SansNarrow-Regular.ttf'
    return ImageFont.truetype(str(FONTS / name), size)


def panel(bright: dict, dark: bool) -> Image.Image:
    img = Image.new('RGB', (W, H), bright['window'])
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(
        (M, M, W - M, H - M), radius=2, fill=bright['window'],
        outline=bright['outline'], width=1,
    )
    d.rectangle((M + 1, M + 1, M + 240, H - M - 1), fill=bright['sidebar'])

    # 侧栏：国徽色块 + 五星导航
    d.rectangle((M + 24, 48, M + 60, 84), fill=bright['primary'])
    star(d, M + 42, 66, 11, bright['gold_pale'])
    d.text((M + 72, 50), 'СССР', font=font(26, True), fill=bright['text'])
    d.text((M + 72, 78), 'Clash of the Soviets', font=font(15),
           fill=bright['text_dim'])
    for i, label in enumerate(NAV):
        y = 140 + i * 48
        active = i == 0
        if active:
            d.rectangle((M + 1, y - 10, M + 241, y + 30), fill=bright['card_alt'])
            d.rectangle((M + 1, y - 10, M + 5, y + 30), fill=bright['primary'])
        star(d, M + 34, y + 10, 7,
             bright['gold'] if active else bright['text_dim'])
        d.text((M + 56, y - 4), label, font=font(18, active),
               fill=bright['text'] if active else bright['text_dim'])

    # 顶栏
    d.text((300, 44), 'ПРОКСИ', font=font(30, True), fill=bright['text'])
    d.text((300, 82), 'ГРУППА: ВСЕ УЗЛЫ', font=font(14), fill=bright['text_dim'])
    for i, (label, fg) in enumerate(
        [('v0.9.2', bright['on_primary']), ('GPL-3.0', bright['text_dim'])]
    ):
        x = 760 + i * 96
        bg = bright['primary'] if i == 0 else bright['card_alt']
        tw = d.textlength(label, font=font(14, True))
        d.rectangle((x, 46, x + tw + 26, 74), fill=bg)
        d.text((x + 13, 51), label, font=font(14, True), fill=fg)

    # 三色旗分隔
    d.rectangle((300, 106, 396, 109), fill=bright['primary'])
    d.rectangle((396, 106, 462, 109), fill=bright['gold'])
    d.rectangle((462, 106, 600, 109), fill=bright['text'] if dark else '#14100F')

    # 节点卡片
    card(d, bright, (300, 126, 790, 330))
    for i, (name, ms, good) in enumerate(NODES):
        y = 146 + i * 46
        if i == 0:
            d.rectangle((302, y - 8, 788, y + 38), fill=bright['primary'])
            fg, sub = bright['on_primary'], bright['on_primary']
        else:
            fg, sub = bright['text'], bright['text_dim']
        star(d, 320, y + 8, 8, bright['gold'] if i else bright['paper'])
        d.text((346, y - 4), name, font=font(19, True), fill=fg)
        d.text((346, y + 20), 'Trojan · TLS 1.3', font=font(13), fill=sub)
        tw = d.textlength(ms, font=font(15, True))
        d.text((768 - tw, y + 4), ms, font=font(15, True), fill=fg)

    # 流量卡片
    card(d, bright, (300, 344, 790, 500))
    d.text((322, 362), 'ТРАФИК', font=font(15, True), fill=bright['text_dim'])
    upload, download = 182.4, 1.284
    d.text((322, 386), 'ОТДАНО 182.4 МиБ', font=font(18, True),
           fill=bright['gold'])
    d.text((536, 386), 'ПРИНЯТО 1.28 ГиБ', font=font(18, True),
           fill=bright['primary'])
    points = [0.7, 0.52, 0.61, 0.35, 0.44, 0.22, 0.3, 0.14, 0.2, 0.09]
    step = 440 / (len(points) - 1)
    path = [(330 + i * step, 478 - v * 62) for i, v in enumerate(points)]
    d.line(path, fill=bright['primary'], width=2)
    d.polygon([*path, (path[-1][0], 478), (path[0][0], 478)],
              fill=hex2rgb(bright['primary'], 38))

    # 右列：连接状态
    card(d, bright, (806, 126, 1092, 500))
    d.text((828, 146), 'СОСТОЯНИЕ', font=font(15, True), fill=bright['text_dim'])
    d.text((828, 170), 'СОЕДИНЕНО', font=font(22, True), fill=bright['gold'])
    d.text((828, 200), 'TUN · СИСТ. ПРОКСИ', font=font(14),
           fill=bright['text_dim'])
    for i, label in enumerate(['СИСТЕМНЫЙ ПРОКСИ', 'ТУННЕЛЬ', 'ПРАВИЛА']):
        y = 244 + i * 46
        d.text((828, y), label, font=font(15), fill=bright['text'])
        on = i != 2
        track = (978, y + 2, 1064, y + 22)
        d.rectangle(track, fill=bright['card_alt'])
        if on:
            d.rectangle(track, fill=bright['primary'])
            d.rectangle((1042, y + 2, 1064, y + 22), fill=bright['on_primary'])
    d.text((828, 400), 'ПРОКСИ ГРУППА', font=font(14, True), fill=bright['text_dim'])
    d.text((828, 424), 'СССР · АВТО', font=font(19, True), fill=bright['text'])

    # 主按钮
    btn = (300, 520, 566, 574)
    d.rectangle(btn, fill=bright['primary'])
    label = 'ПОДКЛЮЧИТЬСЯ'
    tw = d.textlength(label, font=font(19, True))
    d.text((btn[0] + (266 - tw) / 2, 537), label, font=font(19, True),
           fill=bright['on_primary'])
    d.rectangle((586, 520, 700, 574), fill=bright['card_alt'])
    d.text((612, 537), 'ПРОВЕРКА', font=font(17, True), fill=bright['text'])

    # 口号横幅
    d.rectangle((300, 596, 1092, 640), fill=bright['primary'])
    d.line([(312, 596), (1080, 596)], fill=bright['gold'], width=2)
    d.line([(300, 640), (1092, 640)], fill=bright['gold'], width=2)
    motto = 'СЛАВА ТРУДУ · ПРОЛЕТАРИИ ВСЕХ СТРАН, СОЕДИНЯЙТЕСЬ!'
    star(d, 322, 618, 8, bright['gold_pale'])
    d.text((344, 605), motto, font=font(19, True), fill=bright['on_primary'])
    return img


def card(d: ImageDraw.ImageDraw, c: dict, box: tuple) -> None:
    d.rectangle(box, fill=c['card'], outline=c['outline'], width=1)


def hex2rgb(value: str, alpha: int = 255) -> tuple:
    value = value.lstrip('#')
    return (
        int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16), alpha
    )


def star(d: ImageDraw.ImageDraw, cx: int, cy: int, r: int, fill: str) -> None:
    import math

    points = []
    for i in range(10):
        radius = r if i % 2 == 0 else r * 0.4
        angle = -math.pi / 2 + i * math.pi / 5
        points.append((cx + radius * math.cos(angle),
                       cy + radius * math.sin(angle)))
    d.polygon(points, fill=fill)


def main() -> None:
    dark = panel(DARK, True)
    light = panel(LIGHT, False)
    dark.save(OUT / 'preview_dark.png')
    light.save(OUT / 'preview_light.png')
    sheet = Image.new('RGB', (W, H * 2 + 16), '#0A0A0A')
    sheet.paste(dark, (0, 0))
    sheet.paste(light, (0, H + 16))
    sheet.save(OUT / 'preview.png')
    print(f'预览已写入 {OUT}')


if __name__ == '__main__':
    main()
