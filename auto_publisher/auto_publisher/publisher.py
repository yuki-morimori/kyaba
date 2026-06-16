"""出品の本体: フォームに商品データを入力して出品する。

安全装置:
  - dry_run: 入力まではするが「出品」ボタンは押さない（確認用）
  - max_per_run: 1回の出品上限
  - ランダム待機: 人間らしい間隔で操作（連続大量出品の検知回避）
  - headed: ブラウザを表示して人が監視
  - 1件失敗しても残りを止めず、結果をログに残す
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Any

from .models import Config, FieldAction, Product


@dataclass
class PublishResult:
    title: str
    status: str          # "published" / "dry_run" / "error" / "skipped"
    detail: str = ""


def _sleep(cfg: Config) -> None:
    """人間らしいランダム待機。"""
    time.sleep(random.uniform(cfg.safety.min_delay_sec, cfg.safety.max_delay_sec))


def _apply_field(page: Any, action: FieldAction, product: Product) -> None:
    """1項目をフォームに反映する。"""
    value = action.resolve(product)
    if action.action == "fill":
        page.fill(action.selector, value)
    elif action.action == "select":
        page.select_option(action.selector, label=value)
    elif action.action == "upload":
        page.set_input_files(action.selector, value)
    elif action.action == "click":
        page.click(action.selector)
    else:
        raise ValueError(f"未知のaction: {action.action}")


def publish_one(page: Any, cfg: Config, product: Product) -> PublishResult:
    """商品1件を出品（dry_runなら送信しない）。"""
    try:
        page.goto(cfg.listing_url)
        _sleep(cfg)
        for action in cfg.fields:
            _apply_field(page, action, product)
            _sleep(cfg)

        if cfg.safety.dry_run:
            return PublishResult(product.title, "dry_run",
                                 "入力のみ（出品ボタンは押していません）")

        page.click(cfg.submit_selector)
        if cfg.success_selector:
            page.wait_for_selector(cfg.success_selector, timeout=30000)
        _sleep(cfg)
        return PublishResult(product.title, "published", "出品完了")
    except Exception as e:  # 1件失敗しても止めない
        return PublishResult(product.title, "error", f"{type(e).__name__}: {e}")


def run(cfg: Config, products: list[Product]) -> list[PublishResult]:
    """出品をまとめて実行する。"""
    from .browser import launch_context  # 遅延import（playwright未導入でもmodel単体テスト可）

    queue = products[: cfg.safety.max_per_run]
    skipped = products[cfg.safety.max_per_run:]
    results: list[PublishResult] = []

    mode = "確認(dry_run)" if cfg.safety.dry_run else "本番出品"
    print(f"[{cfg.platform}] {mode} / {len(queue)}件を処理"
          f"（上限{cfg.safety.max_per_run}・超過{len(skipped)}件は次回）")

    with launch_context(cfg.safety.user_data_dir, cfg.safety.headed) as context:
        page = context.pages[0] if context.pages else context.new_page()

        # 初回はログインが必要。ログイン画面を開いて人の操作を待つ。
        page.goto(cfg.login_url)
        input("ブラウザでログインを済ませたら、ここでEnterを押してください... ")

        for product in queue:
            res = publish_one(page, cfg, product)
            print(f"  - {res.status:9s} {res.title}  {res.detail}")
            results.append(res)

    for product in skipped:
        results.append(PublishResult(product.title, "skipped", "今回の上限超過"))
    return results
