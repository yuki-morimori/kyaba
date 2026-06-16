"""商品データと設定の読み込み（ブラウザ非依存・単体テスト可能）。"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Product:
    """入力1件（CSVの1行）。出品なら1商品、フォーム記入なら1件分のデータ。

    出品でよく使う列（title/price等）は名前付きで持つが、すべて任意。
    出品以外（申込・登録フォーム等）の任意の列は extra に入る。
    """
    title: str = ""
    price: str = ""
    description: str = ""
    file_path: str = ""
    tags: str = ""
    extra: dict[str, str] = field(default_factory=dict)

    def value_for(self, source: str) -> str:
        """フィールド設定の source 名から値を取り出す（名前付き列→extra の順）。"""
        if source in {"title", "price", "description", "file_path", "tags"}:
            return str(getattr(self, source))
        return self.extra.get(source, "")

    @property
    def label(self) -> str:
        """ログ表示用の名前。title が無ければ最初の値を使う。"""
        if self.title:
            return self.title
        for v in self.extra.values():
            if v:
                return v
        return "(無題)"


def load_products(path: str | Path) -> list[Product]:
    """CSVを読み、Productのリストにする。未知の列は extra に入れる。

    出品用にも、汎用フォーム入力用にも使える（title が無くてもOK）。
    すべての値が空の行だけスキップする。
    """
    known = {"title", "price", "description", "file_path", "tags"}
    products: list[Product] = []
    with Path(path).open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if not any((v or "").strip() for v in row.values()):
                continue  # 完全に空の行のみスキップ
            extra = {k: (v or "").strip() for k, v in row.items()
                     if k and k not in known}
            products.append(Product(
                title=(row.get("title") or "").strip(),
                price=(row.get("price") or "").strip(),
                description=(row.get("description") or "").strip(),
                file_path=(row.get("file_path") or "").strip(),
                tags=(row.get("tags") or "").strip(),
                extra=extra,
            ))
    return products


@dataclass
class FieldAction:
    """フォーム1項目の操作定義。

    by: 要素の探し方。css(既定) / label / placeholder / text。
        BOOTH等の動的フォームは class が毎回変わるので、label や placeholder
        （画面に見えている文言）で指定すると壊れにくい。
    """
    action: str            # fill / select / upload / click
    selector: str          # by に応じて CSSセレクタ or 表示文言
    source: str | None = None   # products.csv の列名
    literal: str | None = None  # 固定値
    by: str = "css"        # css / label / placeholder / text

    def resolve(self, product: Product) -> str:
        """この操作で入力する値を決める（literal優先、なければsource）。"""
        if self.literal is not None:
            return str(self.literal)
        if self.source:
            return product.value_for(self.source)
        return ""


@dataclass
class Safety:
    dry_run: bool = True
    headed: bool = True
    max_per_run: int = 10
    min_delay_sec: float = 4.0
    max_delay_sec: float = 9.0
    user_data_dir: str = ".browser_profile"
    # "chrome"=PCにインストール済みのChromeを使う（chromiumの追加DL不要・推奨）。
    # ""=Playwright同梱のchromiumを使う（要 playwright install chromium）。
    browser_channel: str = "chrome"


@dataclass
class Config:
    platform: str
    login_url: str
    listing_url: str
    submit_selector: str
    fields: list[FieldAction]
    success_selector: str | None = None
    safety: Safety = field(default_factory=Safety)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Config":
        fields = [FieldAction(**f) for f in d.get("fields", [])]
        safety = Safety(**(d.get("safety") or {}))
        return cls(
            platform=d.get("platform", "unknown"),
            login_url=d["login_url"],
            listing_url=d["listing_url"],
            submit_selector=d["submit_selector"],
            fields=fields,
            success_selector=d.get("success_selector"),
            safety=safety,
        )
