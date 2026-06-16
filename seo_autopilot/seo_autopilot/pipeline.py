"""1キーワード → 1記事 を生成するオーケストレーション。

流れ（動画の①〜⑥に対応）:
  ② 構成(build_outline)
  ③ 執筆(write_draft)
  ④ 品質レビュー(review)  →  合格なら終了
  ⑥ リライト(rewrite)     →  threshold を超えるまで最大 max_rewrites 回
最後に frontmatter 付き Markdown を output_dir に保存する。
"""

from __future__ import annotations

import datetime as _dt
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import steps


@dataclass
class Config:
    niche: str
    audience: str
    tone: str
    target_chars: int = 3500
    quality_threshold: float = 0.8
    max_rewrites: int = 2
    model: str = "claude-opus-4-8"
    use_web_search: bool = False
    output_dir: str = "output"

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Config":
        known = {k: d[k] for k in cls.__dataclass_fields__ if k in d}
        return cls(**known)


@dataclass
class Result:
    keyword: str
    outline: dict[str, Any]
    article_md: str
    review: dict[str, Any]
    rewrites: int
    path: Path | None = None
    history: list[dict[str, Any]] = field(default_factory=list)


def _slugify(text: str) -> str:
    """ファイル名用の簡易スラッグ（日本語はそのまま、記号だけ除去）。"""
    text = re.sub(r"[\\/:*?\"<>|\s]+", "-", text.strip())
    return text[:60] or "article"


def _save(cfg: Config, res: Result) -> Path:
    out_dir = Path(cfg.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    today = _dt.date.today().isoformat()
    path = out_dir / f"{today}_{_slugify(res.keyword)}.md"

    o = res.outline
    related = ", ".join(o.get("related_keywords", []))
    frontmatter = (
        "---\n"
        f"title: \"{o.get('title', '')}\"\n"
        f"description: \"{o.get('meta_description', '')}\"\n"
        f"primary_keyword: \"{o.get('primary_keyword', res.keyword)}\"\n"
        f"related_keywords: \"{related}\"\n"
        f"quality_score: {res.review.get('overall', 0):.2f}\n"
        f"rewrites: {res.rewrites}\n"
        f"date: {today}\n"
        "draft: true\n"  # 人の最終監修を前提に下書き扱いで出す
        "---\n\n"
    )
    path.write_text(frontmatter + res.article_md + "\n", encoding="utf-8")
    return path


def generate(client, cfg: Config, keyword: str, notes: str = "") -> Result:
    """1記事ぶんのパイプラインを実行する。"""
    sys_blocks = steps._system_blocks(cfg.niche, cfg.audience, cfg.tone)
    history: list[dict[str, Any]] = []

    print(f"\n=== [{keyword}] ② 構成を作成 ===")
    outline = steps.build_outline(
        client, cfg.model, sys_blocks, keyword, notes, cfg.target_chars)
    print(f"  タイトル: {outline.get('title')}")

    print(f"\n=== [{keyword}] ③ 本文を執筆 ===")
    article = steps.write_draft(
        client, cfg.model, sys_blocks, outline, cfg.target_chars)

    rewrites = 0
    review = steps.review(client, cfg.model, sys_blocks, article, keyword)
    history.append({"stage": "draft", "review": review})
    print(f"\n=== [{keyword}] ④ 品質レビュー: 総合 {review['overall']:.2f} ===")

    while review["overall"] < cfg.quality_threshold and rewrites < cfg.max_rewrites:
        rewrites += 1
        print(f"\n=== [{keyword}] ⑥ リライト {rewrites}回目 "
              f"（{review['overall']:.2f} < {cfg.quality_threshold}）===")
        for i in review["issues"]:
            print(f"  - {i}")
        article = steps.rewrite(
            client, cfg.model, sys_blocks, article, review["issues"], cfg.target_chars)
        review = steps.review(client, cfg.model, sys_blocks, article, keyword)
        history.append({"stage": f"rewrite{rewrites}", "review": review})
        print(f"\n=== [{keyword}] ④ 再レビュー: 総合 {review['overall']:.2f} ===")

    res = Result(keyword, outline, article, review, rewrites, history=history)
    res.path = _save(cfg, res)
    print(f"\n✓ 保存: {res.path}  (総合 {review['overall']:.2f}, "
          f"リライト {rewrites}回)")
    return res
