@echo off
chcp 65001 >nul
REM === 自動出品ツール 起動メニュー（Windows）===
cd /d "%~dp0"

if not exist config.yaml (
  echo config.yaml がありません。config.example.yaml または config.booth.yaml を
  echo config.yaml という名前でコピーして、出品先に合わせて編集してください。
  pause
  exit /b 1
)

echo どれを実行しますか？
echo   1) 下見（ブラウザを開かず入力内容だけ表示）
echo   2) 確認モード（入力するが出品しない）
echo   3) 本番出品
set /p mode="番号を入力してEnter: "

if "%mode%"=="1" python run.py --plan
if "%mode%"=="2" python run.py
if "%mode%"=="3" python run.py --live
pause
