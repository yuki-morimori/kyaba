# SEO自動運転パイプライン（Claude Code記事量産）

分析した広告動画（DOTAIの「Claude Code × SEO自動運転」）と**同じ“型”**を、
あなたのジャンルで回すための最小実装です。1キーワードを入れると、
動画の流れ（①情報収集 → ②構成 → ③執筆 → ④品質レビュー → ⑥リライト/改善）を
自動で実行し、frontmatter付きMarkdown記事を出力します。

```
キーワード → ②構成案(JSON) → ③本文執筆 → ④品質採点 ──合格──▶ 保存(draft)
                                          └─不合格→⑥リライト→再採点(最大N回)
```

## なぜこの構成か
- **②構成・④レビュー** は構造化出力（`output_config.format`）でJSONを確実に受け取る
- **③執筆・⑥リライト** は長文なのでストリーミング生成
- 全ステップ adaptive thinking + `effort: high` で品質優先
- レビューが閾値未満なら**自動でリライトを回す**＝動画の「KPIを自分で判断して改善」に相当
- 出力は必ず `draft: true`：**AIの量産記事はそのまま公開せず、人の監修を前提**にしています（SEO・景表法リスク対策）

## セットアップ
```bash
cd seo_autopilot
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...   # https://console.anthropic.com で取得
```

## 使い方
```bash
# keywords.csv のキーワードをまとめて記事化
python run.py

# 単発で試す
python run.py --keyword "ものづくり補助金 採択率" --notes "採択率を上げるコツ中心で"
```
生成物は `output/YYYY-MM-DD_キーワード.md` に保存されます。

## 自分のジャンルへ差し替える（重要）
動画と同じ商材を作る必要はありません。`config.yaml` の3つを書き換えるだけで横展開できます。

| 項目 | 役割 | 例 |
|---|---|---|
| `niche` | メディアのテーマ | 相続 / BtoB SaaS比較 / 特定業界の求人 |
| `audience` | 想定読者 | 個人事業主 / 情シス担当者 |
| `tone` | 文体・方針 | 専門的・誇張なし・根拠重視 |

`keywords.csv` に狙うキーワードと編集メモを並べれば、その分だけ記事が量産されます。

## ファイル構成
```
seo_autopilot/
├── run.py                 # 実行エントリ（CLI）
├── config.yaml            # ニッチ・読者・トーン・閾値の設定
├── keywords.csv           # 入力キーワード一覧
├── requirements.txt
├── .env.example
└── seo_autopilot/
    ├── client.py          # Anthropicクライアント（モデル: claude-opus-4-8）
    ├── prompts.py         # 各ステップのプロンプト＋JSONスキーマ
    ├── steps.py           # 構成/執筆/レビュー/リライトのAPI呼び出し
    └── pipeline.py        # ①〜⑥のオーケストレーション＋保存
```

## コスト・運用の目安
- モデルは Opus 4.8（最高品質）。コスト重視なら `config.yaml` の `model` を
  `claude-sonnet-4-6` に変更すると安く速くなります（品質はやや下がる）。
- 1記事あたり 構成1 + 執筆1 + レビュー(1+リライト回数) のAPI呼び出し。
- 大量バッチで動かすなら Batches API（50%オフ・非同期）への置き換えも可能です。

## 注意（必読）
- **公開前に必ず人が監修**してください。独自情報・一次情報・体験を足すほどSEOで強くなります。
- 制度・数値・実績は**自分の本物のデータ**で。「必ず稼げる」等の断定は景表法・各媒体ポリシー違反になりがちです。
- AIの大量生成だけに頼った薄い記事はGoogleに評価されません。「自動運転」でも監修は外さないこと。
