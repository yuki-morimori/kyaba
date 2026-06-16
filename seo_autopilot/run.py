#!/usr/bin/env python3
"""SEO自動運転パイプラインの実行エントリ。

使い方:
  # 1) 依存をインストール
  pip install -r requirements.txt

  # 2) APIキーを設定（https://console.anthropic.com で取得）
  export ANTHROPIC_API_KEY=sk-ant-...

  # 3) keywords.csv のキーワードをまとめて記事化
  python run.py

  # 単発でキーワードを指定して試す
  python run.py --keyword "ものづくり補助金 採択率"

生成物は output/ に Markdown（frontmatter付き・draft: true）で保存される。
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import yaml

from seo_autopilot.client import get_client
from seo_autopilot.pipeline import Config, generate

HERE = Path(__file__).parent


def load_config(path: Path) -> Config:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return Config.from_dict(data)


def load_keywords(path: Path) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    with path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            kw = (row.get("keyword") or "").strip()
            if kw:
                rows.append((kw, (row.get("notes") or "").strip()))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description="Claude Code SEO自動運転パイプライン")
    ap.add_argument("--config", default=str(HERE / "config.yaml"))
    ap.add_argument("--keywords", default=str(HERE / "keywords.csv"))
    ap.add_argument("--keyword", help="単発実行するキーワード（指定時はCSVを無視）")
    ap.add_argument("--notes", default="", help="--keyword と併用する編集メモ")
    args = ap.parse_args()

    cfg = load_config(Path(args.config))
    client = get_client()

    if args.keyword:
        queue = [(args.keyword, args.notes)]
    else:
        queue = load_keywords(Path(args.keywords))

    if not queue:
        print("キーワードがありません。keywords.csv を確認してください。", file=sys.stderr)
        return 1

    print(f"ニッチ: {cfg.niche} / モデル: {cfg.model} / {len(queue)}件を処理します。")
    for kw, notes in queue:
        try:
            generate(client, cfg, kw, notes)
        except Exception as e:  # 1件失敗しても残りを止めない
            print(f"!! [{kw}] 失敗: {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
