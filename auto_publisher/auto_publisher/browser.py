"""Playwrightブラウザの起動（ログイン済みセッションを再利用）。

playwright は遅延importにして、未インストール環境でも models 等の
単体テストが通るようにしている。
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path


@contextmanager
def launch_context(user_data_dir: str, headed: bool = True):
    """永続コンテキストでブラウザを起動する。

    user_data_dir にセッション（Cookie等）が保存されるので、
    最初に手動ログインすれば次回以降はログイン状態が再利用される。
    → 認証情報を自前で平文保存しないための設計。
    """
    from playwright.sync_api import sync_playwright  # 遅延import

    Path(user_data_dir).mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=not headed,
        )
        try:
            yield context
        finally:
            context.close()
