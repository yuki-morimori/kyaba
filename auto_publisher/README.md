# RPA自動出品ツール（デジタル商品向け）

デジタル商品（テンプレ・データ・プロンプト集など）を、自分のショップに
**RPA（ブラウザ自動操作）で自動出品**するツールです。
出品先をベタ書きせず、**設定ファイルでどのサイトにも対応できる汎用設計**にしています。

> このツール自体が「データ商品」として売れます（同梱の `products.csv` の3つ目）。
> 「データ販売 ＋ その自動化ツールも売る」という二段構えに使えます。

```
products.csv（商品一覧） → ブラウザ自動操作で出品フォームに入力 → 出品
```

## ⚠️ 必ず守ること（規約・リスク）
- **自分のショップ・自分の商品にのみ**使ってください。
- **推奨出品先＝自分のショップ型のデジタル販売所**：BOOTH / Gumroad / BASE / STORES など。
  これらは「自分の店に自分の商品を並べる」ので規約リスクが低い。
- **メルカリ / ラクマ等のC2Cは非推奨**：自動化（bot）が規約で禁止されており、
  アカウント停止のリスクがあります。デジタルデータ販売自体も禁止の場合があります。
- 公式APIがある出品先（BASE/Gumroad等）は、本RPAより**APIの方が安全で壊れにくい**です。
  まずAPIが使えないか確認を。
- 連続大量出品は避け、`max_per_run` と待機時間で人間らしく。

## セットアップ
```bash
cd auto_publisher
pip install -r requirements.txt
python -m playwright install chromium      # 初回のみ
cp config.example.yaml config.yaml          # 出品先に合わせて編集
```

## 出品先の設定（config.yaml）
`config.example.yaml` を見ながら、出品先の以下を埋めます。
- `login_url` / `listing_url`：ログイン画面と新規出品フォームのURL
- `fields`：各入力欄の **CSSセレクタ** と、`products.csv` のどの列を入れるか
  - セレクタはブラウザの検証(F12)で入力欄を右クリック → Copy selector
- `submit_selector`：出品確定ボタン
- `safety`：安全装置（下記）

## 使い方
```bash
# 1) ブラウザを起動せず、何をどの欄に入れるか下見（一番安全）
python run.py --plan

# 2) 確認モード（入力するが「出品」ボタンは押さない）
python run.py
#   → ブラウザが開く → 手動でログイン → Enter → 各商品を自動入力（送信はしない）

# 3) 確認できたら本番出品
python run.py --live
```

## 安全装置（config.yaml の safety）
| 設定 | 役割 |
|---|---|
| `dry_run: true` | 入力するが出品ボタンを押さない（確認用）。`--live` で解除 |
| `headed: true` | ブラウザを表示して人が監視 |
| `max_per_run` | 1回の出品上限（連続大量出品を防ぐ） |
| `min/max_delay_sec` | 各操作のランダム待機（人間らしく） |
| `user_data_dir` | ログイン済みセッションを保存（認証情報は平文保存しない） |

初回に手動ログインすれば、そのセッションが `user_data_dir` に保存され、
次回以降はログイン状態が再利用されます（ID/パスワードをコードに書きません）。

## ファイル構成
```
auto_publisher/
├── run.py                 # 実行エントリ（--plan / --live）
├── config.example.yaml    # 出品先ごとの設定テンプレ
├── products.csv           # 出品する商品一覧
├── requirements.txt
└── auto_publisher/
    ├── models.py          # 商品・設定の読み込み（ブラウザ非依存）
    ├── browser.py         # Playwright起動（セッション再利用）
    └── publisher.py       # 出品本体＋安全装置
```

## 注意
- 出品先のフォームやセレクタは変わることがあります。動かなくなったら `config.yaml` を見直してください。
- 本ツールは出品作業の効率化が目的です。販売する商品・表記は各サイトの規約と法令（特商法等）に従ってください。
