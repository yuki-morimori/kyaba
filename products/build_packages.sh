#!/usr/bin/env bash
# 販売用の配布zipを作る。
#   使い方:  bash products/build_packages.sh
#   出力先:  products/dist/*.zip
# 開発用のゴミ（キャッシュ・個人セッション・自分のconfig）は除外する。
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST="$ROOT/products/dist"
mkdir -p "$DIST"

# 配布物に含めない（個人情報・環境依存・キャッシュ）
EXCLUDES=(
  -x "*/__pycache__/*" "*.pyc"
  -x "*/.browser_profile/*"
  -x "*/config.yaml"          # 各自が作るので同梱しない（example は同梱）
  -x "*/.git/*" "*/dist/*" "*/output/*" "*/assets/*"
)

pack () {  # pack <フォルダ名> <zip名>
  local src="$1" name="$2"
  ( cd "$ROOT" && zip -r -q "$DIST/$name" "$src" "${EXCLUDES[@]}" )
  echo "  ✓ $DIST/$name"
}

echo "配布zipを作成します..."
pack "auto_publisher" "auto_publisher_v1.zip"
pack "seo_autopilot"  "seo_autopilot_v1.zip"

echo "完了。products/dist/ をそのまま出品ページにアップロードできます。"
