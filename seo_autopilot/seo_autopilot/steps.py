"""パイプラインの各ステップ（Claude API呼び出し本体）。

- 構成/レビュー: 構造化出力（messages.parse）でJSONを確実に受け取る。
- 執筆/リライト: 長文になるのでストリーミングで生成する。
すべて adaptive thinking + effort を使い、品質を最優先にする。
"""

from __future__ import annotations

import json
from typing import Any

from . import prompts


def _system_blocks(niche: str, audience: str, tone: str) -> list[dict[str, Any]]:
    """共通システムプロンプトをキャッシュ可能なブロックとして返す。"""
    return [
        {
            "type": "text",
            "text": prompts.system_prompt(niche, audience, tone),
            "cache_control": {"type": "ephemeral"},
        }
    ]


def _structured(client, model, sys_blocks, user_prompt, schema) -> dict[str, Any]:
    """構造化出力でJSONを取得する共通処理。

    output_config.format でスキーマを強制し、テキストブロックをjson.loadsする。
    thinking が先頭に来てもよいよう type=="text" のブロックを拾う。
    """
    resp = client.messages.create(
        model=model,
        max_tokens=4000,
        thinking={"type": "adaptive"},
        output_config={
            "effort": "high",
            "format": {"type": "json_schema", "schema": schema},
        },
        system=sys_blocks,
        messages=[{"role": "user", "content": user_prompt}],
    )
    text = next(b.text for b in resp.content if b.type == "text")
    return json.loads(text)


def build_outline(client, model, sys_blocks, keyword, notes, target_chars) -> dict[str, Any]:
    """②構成: 構造化出力で見出し構成を取得。"""
    return _structured(
        client, model, sys_blocks,
        prompts.outline_prompt(keyword, notes, target_chars),
        prompts.OUTLINE_SCHEMA,
    )


def write_draft(client, model, sys_blocks, outline: dict[str, Any], target_chars) -> str:
    """③執筆: ストリーミングで本文を生成。"""
    outline_json = json.dumps(outline, ensure_ascii=False, indent=2)
    parts: list[str] = []
    with client.messages.stream(
        model=model,
        max_tokens=16000,
        thinking={"type": "adaptive"},
        output_config={"effort": "high"},
        system=sys_blocks,
        messages=[{"role": "user", "content": prompts.draft_prompt(
            outline_json, target_chars)}],
    ) as stream:
        for text in stream.text_stream:
            parts.append(text)
            print(text, end="", flush=True)
    print()
    return "".join(parts).strip()


def review(client, model, sys_blocks, article_md: str, keyword: str) -> dict[str, Any]:
    """④品質レビュー: 構造化出力でスコアと改善点を取得。"""
    return _structured(
        client, model, sys_blocks,
        prompts.review_prompt(article_md, keyword),
        prompts.REVIEW_SCHEMA,
    )


def rewrite(client, model, sys_blocks, article_md: str, issues, target_chars) -> str:
    """⑥リライト/改善: 指摘を反映して書き直す（ストリーミング）。"""
    parts: list[str] = []
    with client.messages.stream(
        model=model,
        max_tokens=16000,
        thinking={"type": "adaptive"},
        output_config={"effort": "high"},
        system=sys_blocks,
        messages=[{"role": "user", "content": prompts.rewrite_prompt(
            article_md, issues, target_chars)}],
    ) as stream:
        for text in stream.text_stream:
            parts.append(text)
            print(text, end="", flush=True)
    print()
    return "".join(parts).strip()
