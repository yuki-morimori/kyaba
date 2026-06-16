@echo off
REM ============================================================
REM  自動出品ツール（買い手はこれをダブルクリックするだけ）
REM  Pythonは同梱しているのでインストール不要です。
REM ============================================================
cd /d "%~dp0"

set PY=python\python.exe

REM Chromiumを同梱している場合はそのパスを使う（無ければPCのChromeを使用）
if exist "ms-playwright" set PLAYWRIGHT_BROWSERS_PATH=%~dp0ms-playwright

if not exist "%PY%" (
  echo 同梱のPythonが見つかりません。フォルダを解凍し直してください。
  pause & exit /b 1
)

if not exist "設定.yaml" (
  echo 「設定.yaml」がありません。付属の説明書をご確認ください。
  pause & exit /b 1
)

echo ============================================
echo   自動出品ツール
echo ============================================
echo   1) 下見    （ブラウザを開かず、入力内容だけ確認）
echo   2) 確認    （入力するが出品はしない）
echo   3) 本番出品（実際に出品する）
echo.
set /p mode="番号を入力してEnter: "

if "%mode%"=="1" "%PY%" app\run.py --plan  --config 設定.yaml --products 商品リスト.csv
if "%mode%"=="2" "%PY%" app\run.py         --config 設定.yaml --products 商品リスト.csv
if "%mode%"=="3" "%PY%" app\run.py --live   --config 設定.yaml --products 商品リスト.csv
echo.
pause
