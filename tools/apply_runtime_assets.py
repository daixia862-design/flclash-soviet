"""把苏联主题素材应用到「已构建」的 FlClash 上——不需要 Flutter 环境，也不需要重新编译。

做的事情：
1. 替换 data/flutter_assets/assets/images 下的图标、头像、托盘图标；
2. 拷入 PT Sans Narrow 与 Noto Sans SC Black，并注册进 FontManifest.json；
3. 把 %APPDATA%/com.follow/clash/shared_preferences.json 里 "flutter.config"
   的 themeProps 改成苏联红种子 + 浅色奶油纸 + 海报字体。

注意：FlClash 运行时这些文件被内存映射锁定（WinError 1224），脚本会跳过并提示；
      配置文件也会在退出时被应用回写，所以务必先关掉 FlClash 再跑。

用法：
  python apply_runtime_assets.py --built "C:/FlClash"
  python apply_runtime_assets.py --built "C:/FlClash" --no-theme   # 只换素材
  python apply_runtime_assets.py --built "C:/FlClash" --restore    # 还原
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
OVERLAY_IMAGES = REPO / 'overlay' / 'assets' / 'images'
OVERLAY_FONTS = REPO / 'overlay' / 'assets' / 'fonts'

FONT_FAMILIES = {
    'PTSansNarrow': [
        {
            'asset': 'assets/fonts/PTSansNarrow-Regular.ttf',
        },
        {
            'asset': 'assets/fonts/PTSansNarrow-Bold.ttf',
            'weight': 700,
        },
    ],
    'SovietPoster': [
        {
            'asset': 'assets/fonts/NotoSansSC-Black.otf',
        },
    ],
}

SOVIET_THEME = {
    'primaryColor': 0xFFC1121F,
    'primaryColors': [
        0xFFC1121F,
        0xFF7F0D13,
        0xFFE63946,
        0xFFE8B21C,
        0xFFB98A00,
        0xFF4C5561,
        0xFF8C1C13,
        0xFFEDE3D0,
    ],
    'themeMode': 'light',
    'colorStyle': 'vivid',
    'pureBlack': False,
    'sidebarBlur': False,
    'liquidGlass': 'none',
    'systemFontFamily': 'SovietPoster',
}

IMAGE_FILES = [
    'assets/images/icon.png',
    'assets/images/icon.ico',
    'assets/images/avatar/arue.jpg',
    'assets/images/avatar/june2.jpg',
    'assets/images/tray/windows/status_1.ico',
    'assets/images/tray/windows/status_2.ico',
    'assets/images/tray/windows/status_3.ico',
    'assets/images/tray/windows/status_4.ico',
    'assets/images/soviet/banner.png',
    'assets/images/soviet/emblem.png',
    'assets/images/soviet/flag.png',
    'assets/images/soviet/header_lenin.png',
    'assets/images/soviet/poster_lenin.jpg',
    'assets/images/soviet/poster_stalin.jpg',
    'assets/images/soviet/skyline.png',
    'assets/images/soviet/star.png',
]


def default_prefs() -> Path:
    appdata = os.environ.get('APPDATA') or str(Path.home() / 'AppData' / 'Roaming')
    return Path(appdata) / 'com.follow' / 'clash' / 'shared_preferences.json'


def app_running() -> bool:
    if os.name != 'nt':
        return False
    try:
        out = os.popen('tasklist /FI "IMAGENAME eq FlClash.exe" /NH').read()
    except OSError:
        return False
    return 'FlClash.exe' in out


def copy_file(src: Path, dst: Path, backup_root: Path, dry: bool) -> str:
    if not src.exists():
        return f'缺素材 {src.relative_to(REPO)}'
    if dry:
        return f'将写入 {dst.name}'
    if dst.exists():
        rel = dst.relative_to(backup_root)
        if not (backup_root / rel).exists():
            (backup_root / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dst, backup_root / rel)
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copy2(src, dst)
    except OSError as error:
        return f'被占用（先关 FlClash）：{dst.name} -> {error.winerror}'
    return f'ok {dst.name}'


def register_fonts(fonts_dir: Path, dry: bool) -> str:
    manifest_path = fonts_dir.parent / 'FontManifest.json'
    if not manifest_path.exists():
        return '未找到 FontManifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    families = {item.get('family') for item in manifest}
    added = []
    for family, faces in FONT_FAMILIES.items():
        if family in families:
            continue
        if not all((fonts_dir.parent / face['asset']).exists() for face in faces):
            continue
        manifest.append({'family': family, 'fonts': faces})
        added.append(family)
    if not added:
        return '字体已注册'
    if not dry:
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False),
            encoding='utf-8',
        )
    return '注册 ' + ', '.join(added)


def patch_prefs(prefs: Path, dry: bool) -> str:
    if not prefs.exists():
        return f'未找到 {prefs}（先启动一次 FlClash 让配置文件生成）'
    raw = json.loads(prefs.read_text(encoding='utf-8'))
    key = 'flutter.config'
    if key not in raw:
        return '配置里没有 flutter.config'
    config = json.loads(raw[key])
    theme = dict(config.get('themeProps') or {})
    theme.update(SOVIET_THEME)
    config['themeProps'] = theme
    raw[key] = json.dumps(config, ensure_ascii=False)
    if not dry:
        backup = prefs.with_suffix('.json.soviet-backup')
        if not backup.exists():
            shutil.copy2(prefs, backup)
        prefs.write_text(json.dumps(raw, ensure_ascii=False), encoding='utf-8')
    return '主题配置已写入'


def restore(built: Path, prefs: Path) -> None:
    backup_root = built / '.soviet-backup'
    if not backup_root.exists():
        print('没有备份可还原')
        return
    count = 0
    for src in backup_root.rglob('*'):
        if not src.is_file():
            continue
        dst = built / 'data' / 'flutter_assets' / src.relative_to(backup_root)
        if src.name == 'FontManifest.json':
            dst = built / 'data' / 'flutter_assets' / 'FontManifest.json'
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        count += 1
    print(f'已还原 {count} 个文件（配置备份见 {prefs}.soviet-backup）')


def main() -> int:
    parser = argparse.ArgumentParser(description='给已构建的 FlClash 换苏联主题素材')
    parser.add_argument('--built', required=True, help='FlClash 安装/解压目录')
    parser.add_argument('--prefs', default=None, help='shared_preferences.json 路径')
    parser.add_argument('--no-theme', action='store_true', help='只换素材，不动配置')
    parser.add_argument('--restore', action='store_true', help='用备份还原')
    parser.add_argument('--dry-run', action='store_true', help='只打印计划')
    args = parser.parse_args()

    built = Path(args.built).expanduser().resolve()
    assets = built / 'data' / 'flutter_assets'
    if not (assets / 'FontManifest.json').exists():
        print(f'这不是 FlClash 目录（缺 data/flutter_assets）：{built}')
        return 2
    prefs = Path(args.prefs).expanduser() if args.prefs else default_prefs()

    if args.restore:
        restore(built, prefs)
        return 0

    if app_running():
        print('⚠ FlClash 正在运行：图标/字体会因内存映射锁定而跳过，配置也会被回写。')

    backup_root = built / '.soviet-backup'
    for rel in IMAGE_FILES:
        src = REPO / 'overlay' / rel
        dst = assets / rel
        if dst.parent.name == 'soviet' and not dst.parent.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
        print(copy_file(src, dst, backup_root, args.dry_run))

    print(register_fonts(assets / 'assets' / 'fonts', args.dry_run))
    if not args.no_theme:
        print(patch_prefs(prefs, args.dry_run))
    print('完成。启动 FlClash 查看效果。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
