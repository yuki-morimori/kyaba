"""各ステップのプロンプトテンプレート。

動画の流れ（①情報収集 → ②構成 → ③執筆 → ④品質レビュー → ⑥リライト/改善）に対応。
ニッチ・読者・トーンは config.yaml から差し込まれる。
"""

from __future__ import annotations


def system_prompt(niche: str, audience: str, tone: str) -> str:
    """全ステップ共通のシステムプロンプト（メディアの人格を固定）。

    キャッシュを効かせるため、リクエストごとに変わる値（日付・キーワード）は
    ここに入れない。ニッチ等は実行中ずっと固定なのでここに置いてよい。
    """
    return (
        f"あなたは「{niche}」を専門に扱うWebメディアの編集兼ライターです。\n"
        f"読者は{audience}です。\n"
        f"文体・方針: {tone}。\n\n"
        "厳守事項:\n"
        "- 検索ユーザーの検索意図を満たすことを最優先する。\n"
        "- 事実に基づき、断定できないことは断定しない。誇大表現・煽りは禁止。\n"
        "- 制度・数値・要件は『一般論』として書き、最新の公式情報の確認を促す一文を必ず添える。\n"
        "- AIが量産したと分かる薄い内容を避け、独自の切り口・具体例・読者の次の行動を示す。\n"
        "- 出力は指示されたフォーマットのみ。前置きや「承知しました」等は書かない。"
    )


def outline_prompt(keyword: str, notes: str, target_chars: int) -> str:
    """②構成: 見出し構成・タイトル・メタディスクリプションをJSONで作る。"""
    return (
        f"次のキーワードで上位表示を狙うSEO記事の構成案を作ってください。\n\n"
        f"対象キーワード: {keyword}\n"
        f"編集メモ: {notes or '（特になし）'}\n"
        f"目標文字数: 約{target_chars}字\n\n"
        "検索意図を分析し、それを満たす論理的な見出し構成（H2/H3）を設計してください。"
    )


# ②構成ステップの構造化出力スキーマ（messages.parse 用）
OUTLINE_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "description": "32文字前後のSEOタイトル"},
        "meta_description": {"type": "string", "description": "120文字前後のメタdescription"},
        "primary_keyword": {"type": "string"},
        "related_keywords": {"type": "array", "items": {"type": "string"}},
        "search_intent": {"type": "string", "description": "想定検索意図の要約"},
        "headings": {
            "type": "array",
            "description": "記事の見出し構成（出てくる順）",
            "items": {
                "type": "object",
                "properties": {
                    "level": {"type": "string", "enum": ["h2", "h3"]},
                    "text": {"type": "string"},
                    "intent": {"type": "string", "description": "この見出しで満たす意図"},
                },
                "required": ["level", "text", "intent"],
                "additionalProperties": False,
            },
        },
    },
    "required": [
        "title",
        "meta_description",
        "primary_keyword",
        "related_keywords",
        "search_intent",
        "headings",
    ],
    "additionalProperties": False,
}


def draft_prompt(outline_json: str, target_chars: int) -> str:
    """③執筆: 構成に沿って本文をMarkdownで書く。"""
    return (
        "次の構成案に厳密に沿って、SEO記事の本文をMarkdownで執筆してください。\n\n"
        f"=== 構成案(JSON) ===\n{outline_json}\n\n"
        "執筆ルール:\n"
        f"- 目標 約{target_chars}字。\n"
        "- 各見出しの intent を満たす内容を書く。\n"
        "- 冒頭にリード文（記事で分かることを2〜3文で）を置く。\n"
        "- 箇条書き・表を適度に使い、読みやすくする。\n"
        "- キーワードは自然に含める（詰め込みすぎない）。\n"
        "- 最後に『よくある質問』を2〜3個（Q&A形式）と、読者の次の一歩を示すまとめを置く。\n"
        "- 出力はMarkdown本文のみ。frontmatterやコードフェンスで全体を囲まない。"
    )


def review_prompt(article_md: str, keyword: str) -> str:
    """④品質レビュー: 記事を採点し、改善点を構造化して返す。"""
    return (
        "あなたは厳しいSEO編集長です。次の記事を評価してください。\n\n"
        f"対象キーワード: {keyword}\n\n"
        f"=== 記事(Markdown) ===\n{article_md}\n\n"
        "各観点を0.0〜1.0で採点し、具体的な改善指示を挙げてください。甘く付けないこと。"
    )


# ④品質レビューの構造化出力スキーマ
REVIEW_SCHEMA = {
    "type": "object",
    "properties": {
        "scores": {
            "type": "object",
            "properties": {
                "search_intent_match": {"type": "number", "description": "検索意図充足 0-1"},
                "accuracy": {"type": "number", "description": "正確性・誇大表現のなさ 0-1"},
                "depth_originality": {"type": "number", "description": "独自性・深さ 0-1"},
                "readability": {"type": "number", "description": "読みやすさ・構成 0-1"},
                "seo_basics": {"type": "number", "description": "タイトル/見出し/キーワード設計 0-1"},
            },
            "required": [
                "search_intent_match",
                "accuracy",
                "depth_originality",
                "readability",
                "seo_basics",
            ],
            "additionalProperties": False,
        },
        "overall": {"type": "number", "description": "総合スコア 0-1"},
        "issues": {
            "type": "array",
            "description": "具体的な改善指示（リライトでそのまま使えるレベルで）",
            "items": {"type": "string"},
        },
    },
    "required": ["scores", "overall", "issues"],
    "additionalProperties": False,
}


def rewrite_prompt(article_md: str, issues: list[str], target_chars: int) -> str:
    """⑥リライト/改善: レビュー指摘を反映して本文を書き直す。"""
    bullet = "\n".join(f"- {i}" for i in issues)
    return (
        "次の記事を、編集長の指摘をすべて反映して改善してください。\n\n"
        f"=== 改善指示 ===\n{bullet}\n\n"
        f"=== 現状の記事(Markdown) ===\n{article_md}\n\n"
        f"ルール: 目標 約{target_chars}字。構成の良さは保ちつつ指摘を解消する。"
        "出力は改善後のMarkdown本文のみ。"
    )
