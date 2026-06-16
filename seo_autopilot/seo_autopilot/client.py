"""Anthropicクライアントの初期化と共通設定。"""

from __future__ import annotations

import anthropic

# Anthropicの最新・最高性能モデル。コスト優先でも勝手に下げない（利用者の判断に委ねる）。
DEFAULT_MODEL = "claude-opus-4-8"


def get_client() -> anthropic.Anthropic:
    """環境変数 ANTHROPIC_API_KEY からキーを解決してクライアントを返す。"""
    # api_key を明示せず環境から解決させるのが推奨（ハードコードしない）。
    return anthropic.Anthropic()
