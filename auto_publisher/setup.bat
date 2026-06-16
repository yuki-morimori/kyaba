@echo off
chcp 65001 >nul
REM === 自動出品ツール 初回セットアップ（Windows）===
REM このファイルをダブルクリックすると必要な準備を自動で行います。
cd /d "%~dp0"

echo [1/2] 必要なライブラリをインストールします...
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo Python が見つからないかもしれません。
  echo https://www.python.org/downloads/ からインストールし、
  echo インストール画面で「Add Python to PATH」にチェックを入れてください。
  pause
  exit /b 1
)

echo [2/2] ブラウザ準備（Chrome利用のため通常はスキップ可）...
python -m playwright install chromium

echo.
echo セットアップ完了！ start.bat をダブルクリックして使い始められます。
pause
