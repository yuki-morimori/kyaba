# プロジェクト・コンテキスト（kyaba / アフィリ・SNS戦略）

> このファイルは会話のたびに追記・更新していく「ユーザーの前提・好み」のメモ。
> 新しいことが分かったら必ずここに反映する。
> ※ ゆうきさんの全体マスター文脈は `C:\Claud BOT\CLAUDE.md`（別マシン側）にある。下記はその要点＋本リポ固有の話。

最終更新: 2026-06-11 (#4 / パイロット=kondate-gacha 決定)

---

## 👤 ユーザー
- 呼び名: **ゆうきさん**。メール: yuuki19951111@gmail.com
- Claude Code と一緒に多数の個人プロダクトを作ってきた（ゲーム・LINE Bot・診断ツール・事業資料など）。
- リポジトリ: `yuki-morimori/kyaba` / 作業ブランチ: `claude/affiliate-sns-strategy-lkbcvj`

## 🧭 応答スタイル（最優先・グローバル設定）
- **結論から先に**。
- **友達風フレンドリー＋敬語ベース**、絵文字を自然に使う。
- 間違いは**迎合せずハッキリ指摘**する。
- UI・成果物は日本語。一般ユーザー/家族向けの分かりやすさ・配慮を重視。

## 💰 コスト方針（CostHawk）
- 見るのは**運用・ランニングコストだけ**。**開発の手間は評価対象外**（クロードコードが引き受ける）。
  - 開発コストに触れる場面では「**ここは僕たちが頑張るよ！**」と添える。
- **無料・ローカル構成を強く好む**。月額が出る選択は基本避ける。
  - 公開: **Cloudflare Pages（無料枠）** / 一時公開: **cloudflared クイックトンネル** / 保存: **OneDrive**。

## 📱 動作環境の好み
- **iPhone実機で確認したい**（5G/モバイル回線でも開ける、**PWA化・ホーム画面追加**を意識）。
- 公開はクリーンに（dev用ファイルを混ぜない）。

## ⚙️ 技術前提（ハマりポイント）
- **TLS傍受環境**: Node系コマンドは `NODE_OPTIONS=--use-system-ca` 必須（無いと `UNABLE_TO_VERIFY_LEAF_SIGNATURE`）。
- Node.js は winget 導入で PATH に無い。シェルは **PowerShell**。常駐は `Start-Process` でデタッチ。
- better-sqlite3 は 12.x。Cloudflare wrangler は OAuth ログイン済み。
- Pages のdev除外は `.assetsignore` 不可 → dist へホワイトリストコピー方式。Pagesは“ソフト404”に注意。
- オフライン/OneDrive閲覧: `fetch('data/*.json')` は file:// で動かない → JSONを `window.__X` 代入の `.js` 化して `<script src>`。

## 🎮 既存の公開済み資産（=SNS入口に転用できる！）
- `cabaret-game`「痛客に貢がせて目指せNo.1キャバ嬢！」育成ゲーム → **https://cabaret.pages.dev/**
- `mahjong-web` 麻雀（一人練習＋四人＋上級yonma_pro） → **https://mahjong-63o.pages.dev/**
- `kondate-gacha` 献立ガチャ(PWA) → **https://kondate-gacha.pages.dev/**
- `nazomono-gacha` 謎もの図鑑ガチャ(PWA) → **https://nazomono-zukan.pages.dev/**
- その他: `muscle-rpg`筋トレRPG / `date-gacha`デートガチャ / `poki-mahjong`(Poki提出用)
- Bot/ツール: 任意時刻LINEリマインドBot / 熱中症アラートBot / `ai-dev-team`(Discord多AI開発チーム)
- 診断/ビジネス: `subsidy-app`補助金 / `joseikin-diagnosis`助成金 / 行政書士マッチング / `good1-agency`事業計画 など

---

## 🎯 このプロジェクトのゴール
- **Claude を活用したアフィリエイト/SNS運用**を始める。
- 条件: **二番煎じにならない独自テーマ**。
- **媒体方針【確定】: SNS入口（集客）＋サイト出口（収益化）の組み合わせ型**。

## 未確定・次回確認したいこと
- [ ] テーマ確定（既存ゲーム資産を入口に使う前提で再検討中）
- [ ] 収益化の優先度（早く稼ぎたい / じっくりブランド化）
- [ ] 使える時間・既存フォロワー等のアセット
- [ ] 顔出し・実名の可否、運用体制（基本1人想定）

## 決定ログ
- 2026-06-11: 媒体は「SNS入口＋サイト出口」の組み合わせ型に決定。
- 2026-06-11: 戦略を確定 → **既存の公開済みゲームを“入口”に、横にアフィリ導線を足す**方式。
- 2026-06-11: **最初のパイロットは `kondate-gacha`**（公開済み・PWA・食材宅配/ふるさと納税ASPが高単価&クリーン&家族向けと一致）。型ができたら cabaret/muscle へ横展開。
- 2026-06-11: 注意点 → cabaret-game のナイト求人ASPはグレー&審査厳。最初はクリーン案件で型づくり。
- 2026-06-11: ⚠️ 本リポ `kyaba` には cabaret-game しか無く、kondate等のコードはローカル `C:\Claud BOT` 側。→ 汎用「アフィリ導線ウィジェット」を `aff-kit/` に作成し、各ゲームへ貼り付け運用。

## 🧰 作ったもの（このリポ）
- `aff-kit/` : どのゲームにも貼れる無料・オフライン安全・PWA対応・ステマ規制対応の広告導線ウィジェット。
