# ============================================================
#  build_windows.ps1
#  買い手に渡す「Python同梱パッケージ」を Windows 上で1回だけ組み立てる。
#  → 買い手は Python のインストール不要。zipを解凍して .bat を押すだけ。
#
#  使い方（Windowsで）:
#    1) このリポジトリ（auto_publisher を含む）を Windows に置く
#    2) PowerShell を開いて、auto_publisher フォルダで:
#         powershell -ExecutionPolicy Bypass -File packaging\build_windows.ps1
#    3) ..\products\dist\自動出品ツール_win.zip が完成 → そのまま販売アップロード
#
#  オプション:
#    -BundleChromium   … Chromiumも同梱（Chromeが無い買い手にも対応・サイズ大 ~+150MB）
#    -PyVersion 3.11.9 … 同梱するPythonのバージョン
#
#  注意: このスクリプトは Windows 専用です（埋め込み版PythonがWindowsバイナリのため）。
# ============================================================
param(
  [string]$PyVersion = "3.11.9",
  [switch]$BundleChromium
)
$ErrorActionPreference = "Stop"

$pkgName = "自動出品ツール"
$here  = Split-Path -Parent $MyInvocation.MyCommand.Path        # packaging\
$proj  = Split-Path -Parent $here                              # auto_publisher\
$build = Join-Path $here "build"
$pkg   = Join-Path $build $pkgName
$distDir = Join-Path (Split-Path -Parent $proj) "products\dist"

Write-Host "== クリーンアップ ==" -ForegroundColor Cyan
if (Test-Path $build) { Remove-Item -Recurse -Force $build }
New-Item -ItemType Directory -Force -Path $pkg     | Out-Null
New-Item -ItemType Directory -Force -Path $distDir | Out-Null

# --- 1. 埋め込み版Pythonを取得・展開 ---
$pyDir = Join-Path $pkg "python"
New-Item -ItemType Directory -Force -Path $pyDir | Out-Null
$pyZip = Join-Path $build "python-embed.zip"
$pyUrl = "https://www.python.org/ftp/python/$PyVersion/python-$PyVersion-embed-amd64.zip"
Write-Host "== 埋め込み版Pythonを取得: $pyUrl ==" -ForegroundColor Cyan
Invoke-WebRequest -Uri $pyUrl -OutFile $pyZip
Expand-Archive -Path $pyZip -DestinationPath $pyDir -Force

# --- 2. pip と site-packages を有効化（._pth を書き換え）---
$tag = ($PyVersion -replace '\.', '').Substring(0,3)   # 3.11.9 -> "311"
$pth = Get-ChildItem $pyDir -Filter "python*._pth" | Select-Object -First 1
@"
python$tag.zip
.
Lib\site-packages

import site
"@ | Set-Content -Encoding ASCII $pth.FullName

# --- 3. pip を導入 ---
$python = Join-Path $pyDir "python.exe"
$getpip = Join-Path $build "get-pip.py"
Write-Host "== pip を導入 ==" -ForegroundColor Cyan
Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile $getpip
& $python $getpip --no-warn-script-location

# --- 4. 依存ライブラリを同梱版Pythonの中へインストール ---
Write-Host "== 依存ライブラリを同梱 ==" -ForegroundColor Cyan
& $python -m pip install --no-warn-script-location playwright pyyaml

# --- 5. （任意）Chromium も同梱 ---
if ($BundleChromium) {
  Write-Host "== Chromium を同梱 ==" -ForegroundColor Cyan
  $env:PLAYWRIGHT_BROWSERS_PATH = Join-Path $pkg "ms-playwright"
  & $python -m playwright install chromium
}

# --- 6. アプリ本体と、買い手向けファイルを配置 ---
Write-Host "== アプリと設定を配置 ==" -ForegroundColor Cyan
$app = Join-Path $pkg "app"
New-Item -ItemType Directory -Force -Path $app | Out-Null
Copy-Item (Join-Path $proj "auto_publisher") (Join-Path $app "auto_publisher") -Recurse
Copy-Item (Join-Path $proj "run.py")          (Join-Path $app "run.py")
# キャッシュは除外
Get-ChildItem $app -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# 買い手に分かりやすい名前で設定・商品・説明を配置
Copy-Item (Join-Path $proj "config.booth.yaml") (Join-Path $pkg "設定.yaml")
Copy-Item (Join-Path $proj "products.csv")       (Join-Path $pkg "商品リスト.csv")
Copy-Item (Join-Path $proj "導入ガイド.md")        (Join-Path $pkg "説明書.md")
Copy-Item (Join-Path $here "出品スタート.bat")      (Join-Path $pkg "出品スタート.bat")

# --- 7. zip 化 ---
$zip = Join-Path $distDir ("{0}_win.zip" -f $pkgName)
if (Test-Path $zip) { Remove-Item $zip }
Compress-Archive -Path $pkg -DestinationPath $zip
Write-Host ""
Write-Host "完成: $zip" -ForegroundColor Green
Write-Host "→ これをそのまま販売ページにアップロードできます（買い手はPython不要）。"
