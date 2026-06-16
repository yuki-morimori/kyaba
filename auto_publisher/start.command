#!/usr/bin/env bash
# === 自動出品ツール 起動メニュー（Mac）===
# 初回のみ: Finderで右クリック→「開く」、またはターミナルで chmod +x start.command
cd "$(dirname "$0")"

# 初回はライブラリ準備（既にあればすぐ終わる）
if ! python3 -c "import playwright, yaml" 2>/dev/null; then
  echo "必要なライブラリをインストールします..."
  python3 -m pip install -r requirements.txt || {
    echo "Python3 が必要です。https://www.python.org/downloads/ からインストールしてください。"
    read -r -p "Enterで閉じる"; exit 1; }
  python3 -m playwright install chromium
fi

if [ ! -f config.yaml ]; then
  echo "config.yaml がありません。config.example.yaml か config.booth.yaml を"
  echo "config.yaml にコピーして編集してください。"
  read -r -p "Enterで閉じる"; exit 1
fi

echo "どれを実行しますか？"
echo "  1) 下見（ブラウザを開かず入力内容だけ表示）"
echo "  2) 確認モード（入力するが出品しない）"
echo "  3) 本番出品"
read -r -p "番号を入力してEnter: " mode
case "$mode" in
  1) python3 run.py --plan ;;
  2) python3 run.py ;;
  3) python3 run.py --live ;;
  *) echo "1〜3を入力してください" ;;
esac
read -r -p "Enterで閉じる"
