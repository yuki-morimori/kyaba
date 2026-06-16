#!/usr/bin/env python3
"""RPA自動出品ツールの実行エントリ。

使い方:
  pip install -r requirements.txt
  python -m playwright install chromium      # 初回のみブラウザ取得
  cp config.example.yaml config.yaml          # 出品先に合わせて編集
  python run.py                               # まずは dry_run（確認モード）

  python run.py --live   # 確認できたら本番出品（config の dry_run も false 推奨）
  python run.py --plan   # ブラウザを起動せず、何を入力するかだけ表示
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

from auto_publisher.models import Config, load_products

HERE = Path(__file__).parent


def load_config(path: Path) -> Config:
    return Config.from_dict(yaml.safe_load(path.read_text(encoding="utf-8")))


def show_plan(cfg: Config, products) -> None:
    """ブラウザを起動せず、各商品で何をどの欄に入れるか表示（安全な下見）。"""
    print(f"[{cfg.platform}] 出品プラン（ブラウザ未起動）")
    for i, p in enumerate(products[: cfg.safety.max_per_run], 1):
        price = f"  (¥{p.price})" if p.price else ""
        print(f"\n#{i} {p.label}{price}")
        for a in cfg.fields:
            print(f"    {a.action:7s} [{a.by}] {a.selector}  ← {a.resolve(p)!r}")
    print(f"\n送信ボタン: {cfg.submit_selector}  "
          f"/ dry_run={cfg.safety.dry_run}")


def main() -> int:
    ap = argparse.ArgumentParser(description="RPA自動出品ツール")
    ap.add_argument("--config", default=str(HERE / "config.yaml"))
    ap.add_argument("--products", default=str(HERE / "products.csv"))
    ap.add_argument("--plan", action="store_true",
                    help="ブラウザを起動せず入力内容だけ表示")
    ap.add_argument("--live", action="store_true",
                    help="本番出品（dry_runを上書きでoffにする）")
    args = ap.parse_args()

    cfg_path = Path(args.config)
    if not cfg_path.exists():
        print(f"設定が見つかりません: {cfg_path}\n"
              f"config.example.yaml を config.yaml にコピーして編集してください。",
              file=sys.stderr)
        return 1

    cfg = load_config(cfg_path)
    products = load_products(args.products)
    if args.live:
        cfg.safety.dry_run = False

    if not products:
        print("商品がありません。products.csv を確認してください。", file=sys.stderr)
        return 1

    if args.plan:
        show_plan(cfg, products)
        return 0

    from auto_publisher.publisher import run
    results = run(cfg, products)

    ok = sum(1 for r in results if r.status in ("published", "dry_run"))
    err = sum(1 for r in results if r.status == "error")
    print(f"\n完了: 成功{ok} / エラー{err} / 全{len(results)}件")
    return 0 if err == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
