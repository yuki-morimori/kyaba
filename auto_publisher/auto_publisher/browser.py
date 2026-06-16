"""Playwrightブラウザの起動（ログイン済みセッションを再利用）。

playwright は遅延importにして、未インストール環境でも models 等の
単体テストが通るようにしている。
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path


@contextmanager
def launch_context(user_data_dir: str, headed: bool = True, channel: str = "chrome"):
    """永続コンテキストでブラウザを起動する。

    user_data_dir にセッション（Cookie等）が保存されるので、
    最初に手動ログインすれば次回以降はログイン状態が再利用される。
    → 認証情報を自前で平文保存しないための設計。

    channel="chrome" ならPCのChromeを使う（chromiumの追加DLが不要）。
    Chromeが無い環境では channel="" にして同梱chromiumを使う。
    """
    from playwright.sync_api import sync_playwright  # 遅延import

    Path(user_data_dir).mkdir(parents=True, exist_ok=True)
    launch_kwargs: dict = {
        "user_data_dir": user_data_dir,
        "headless": not headed,
        # 「自動化されたブラウザ」という痕跡を減らす。
        # ログイン時のreCAPTCHA等のボット判定を通りやすくするため（手動ログイン前提）。
        "ignore_default_args": ["--enable-automation"],
        "args": ["--disable-blink-features=AutomationControlled"],
    }
    if channel:
        launch_kwargs["channel"] = channel

    with sync_playwright() as p:
        try:
            context = p.chromium.launch_persistent_context(**launch_kwargs)
        except Exception:
            # Chromeが見つからない等のときは同梱chromiumにフォールバック
            launch_kwargs.pop("channel", None)
            context = p.chromium.launch_persistent_context(**launch_kwargs)
        try:
            yield context
        finally:
            context.close()
