# aff-kit — ゲームに貼るだけの広告（アフィリエイト）導線キット

既存の公開済みゲーム（kondate-gacha / cabaret-game / muscle-rpg …）の
**結果画面の下に、相性のいい広告リンクを自然に差し込む**ための小さな部品です。

## 特徴（ゆうきさんの前提に合わせてある）
- 🆓 **無料・静的のみ**。バックエンド不要、Cloudflare Pages にそのまま置ける（運用コスト0）。
- 📴 **`fetch` 不使用** → `file://` / OneDrive 直開きでも動く。
- 📱 **スマホ/PWAファースト**（大きめタップ領域・レスポンシブ）。
- ⚖️ **ステマ規制(2023.10〜)対応**：必ず「広告」ラベルを表示（消せない仕様）。
- 📊 **クリック計測**を `localStorage` に簡易記録（成果の最終確認はASP管理画面で）。

## 使い方（3ステップ）

1. `asp-widget.js` を対象ゲームのフォルダにコピー。
2. 結果画面のHTMLに読み込みと設定を追加：

```html
<div id="result"></div>  <!-- 差し込み先 -->
<script src="asp-widget.js"></script>
<script>
  AffKit.render({
    mount: '#result',
    heading: 'この献立、作らずに届けてもらう？🛒',
    items: [
      { id:'oisix', label:'Oisix お試しセット', desc:'下ごしらえ不要で時短。', url:'★自分のアフィリリンク★', badge:'人気' },
    ]
  });
</script>
```

3. `url` を自分のASPアフィリリンクに差し替えるだけ。`demo.html` をブラウザで開けば動作確認できます。

## ゲーム別・相性のいいASPジャンル

| ゲーム | おすすめジャンル | クリーン度 |
|---|---|---|
| `kondate-gacha` 献立 | 食材宅配(Oisix/ヨシケイ等)・ふるさと納税 | ◎ |
| `date-gacha` デート | マッチングアプリ・レストラン予約 | ◎ |
| `muscle-rpg` 筋トレ | プロテイン・ジム・フィットネス | ◎ |
| `mahjong-web` 麻雀 | オンライン麻雀アプリ・麻雀グッズ(Amazon) | ◎ |
| `nazomono-gacha` 謎もの | 知育・書籍・サブスク | ◎ |
| `cabaret-game` キャバ | 美容医療・脱毛・コスメ（ナイト求人は△審査厳） | △ |

## API
- `AffKit.render(opts)` — 広告カードを描画。`opts = { mount, heading, items[], note }`
  - `items[]` の各要素: `{ id, label, desc, url, badge }`
- `AffKit.getClicks()` — `localStorage` に貯めたクリック数を取得（`{id: 回数}`）。

## ASP登録の流れ（最初の準備）
1. **A8.net / もしもアフィリエイト / バリューコマース** あたりに無料登録（審査ゆるめ）。
2. 上表のジャンルで案件を検索 → 提携申請 → 承認後にリンク発行。
3. 発行リンクを `url` に貼る。これで完成。
