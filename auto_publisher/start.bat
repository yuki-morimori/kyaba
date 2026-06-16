@echo off
REM === 自動出品ツール 起動メニュー（Windows）===
cd /d "%~dp0"

REM config.yaml が無ければ BOOTH用テンプレから自動で作る
if not exist config.yaml (
  if exist config.booth.yaml (
    copy config.booth.yaml config.yaml >nul
    echo BOOTH用の設定ファイル config.yaml を作成しました。
    echo あとで出品先に合わせて config.yaml を編集できます。
    echo.
  ) else (
    echo config.yaml も config.booth.yaml も見つかりません。
    pause
    exit /b 1
  )
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
