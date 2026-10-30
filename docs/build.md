# 构建说明（Windows）

实测环境，从零到出包约 40 分钟（下载占大头）：

- Flutter 3.47.6 stable（与上游 `.github/workflows/build.yaml` 里的 `FLUTTER_VERSION` 一致）
- Visual Studio Build Tools 2022（`Microsoft.VisualStudio.Workload.VCTools`，含 MSVC 14.44 与 Windows SDK 10.0.26100）
- Python 3 + Pillow（只在重新生成美术素材时需要）

## 1. 取源码

```powershell
git clone https://github.com/chen08209/FlClash.git
cd FlClash
git checkout v0.9.2
git submodule update --init --recursive   # core/Clash.Meta
```

有子模块就可以正常编译 Go 内核；如果用的是不含子模块的 zip 包（比如 codeload 下的 tag 压缩包），
见下面第 4 条。

## 2. 打主题补丁

```powershell
git apply <这个仓库>\patches\0001-soviet-theme.patch
Copy-Item -Recurse -Force <这个仓库>\overlay\* .
```

`overlay/` 和补丁是等价的（补丁只覆盖文本文件，图片与字体在 `overlay/` 里，因为 Git 的二进制
补丁会让文件膨胀到 25 MB）。

## 3. 符号链接 —— 第一个坑

`flutter build windows` 会先给插件建符号链接，非管理员默认建不了，报：

```
Building with plugins requires symlink support.
Please enable Developer Mode in your system settings.
```

三条路，选一条：

1. 开 Windows 开发者模式（设置 → 系统 → 开发者选项），需要管理员；
2. 以管理员身份跑一次构建；
3. 免管理员的绕法：用 directory junction 手工把 `.plugin_symlinks` 填满。
   Flutter 只检查 `link.existsSync()`，junction 也满足（Dart 会把它当 `Link`）。

```powershell
$root = (Get-Location).Path
$deps = Get-Content .flutter-plugins-dependencies -Raw | ConvertFrom-Json
foreach ($platform in @('windows', 'linux', 'macos')) {
  $items = $deps.plugins.$platform
  if (-not $items) { continue }
  $dir = Join-Path $root "$platform\flutter\ephemeral\.plugin_symlinks"
  New-Item -ItemType Directory -Force -Path $dir | Out-Null
  foreach ($item in $items) {
    $link = Join-Path $dir $item.name
    if (Test-Path $link) { continue }
    New-Item -ItemType Junction -Path $link -Target $item.path | Out-Null
  }
}
```

注意 Flutter 会给 **windows 和 linux 两个平台**都建链接，所以两个目录都得填，否则 linux 那边会报：

```
PathExistsException: Cannot create link, path = '...\linux\flutter\ephemeral\.plugin_symlinks\app_links_linux'
```

## 4. 缺失的 core 产物 —— 第二个坑

`windows/CMakeLists.txt` 的 `install(FILES ...)` 会从 `libclash/windows/` 取三个文件：

```
FlClashCore.exe
FlClashHelperService.exe
manifest.json        # {"coreSha256": "..."}
```

正常流程由 `dart setup.dart windows` 先编 Go 内核再生成它们。如果跳过了这一步（或没有子模块），
CMake 的 install 阶段会报 `file INSTALL cannot find`。两条路：

1. 老实编内核：`dart setup.dart windows`（需要 Go + Rust）；
2. 从官方发布包里解出这三个文件放到 `libclash/windows/`，并在 `pubspec.yaml` 里关掉 hook：

```yaml
hooks:
  user_defines:
    setup:
      build_assets: false
    rust_api:
      build_assets: false
```

另外子模块为空时，`pubspec.yaml` 里声明的 `core/Clash.Meta/component/ca/ca-certificates.crt`
会缺失，从 <https://curl.se/ca/cacert.pem> 下下来放到该路径即可。

## 5. MAX_PATH —— 第三个坑

项目路径一深，MSBuild 就会在 `build\windows\x64\plugins\...\*.tlog` 上报：

```
error MSB3491: 未能向文件“...”写入行。超过 OS 最大路径限制（必须少于 260 个字符）
```

把工程放到短路径下编，例如 `D:\fc\FlClash`：

```powershell
robocopy <源码> D:\fc\FlClash /MIR /XD build .dart_tool .git
```

拷贝后 `.plugin_symlinks` 里的链接可能失效（Dart 既不当 Link 又真实存在），删掉重建一遍
（第 3 条的脚本），再 `flutter pub get`。

## 6. 构建

```powershell
$env:PATH = "C:\dev\flutter\bin;C:\dev\flutter\bin\mingit\cmd;$env:PATH"
$env:PUB_CACHE = "C:\dev\pub_cache"
flutter pub get
flutter build windows --release --no-pub
```

产物在 `build\windows\x64\runner\Release\`。如果目标机缺少运行库，把
`dartjni.dll`、`rust_api.dll`、`FlClashCore.exe` 这些旁挂文件一起拷过去。

## 重新生成美术素材（可选）

图标、托盘、海报、天际线、徽标都是 Python + Pillow 画的，调整配色后重跑生成脚本即可，
不需要动 Dart 代码（脚本里的路径写死了本机目录，按需改）。
