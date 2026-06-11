/*!
 * aff-kit / asp-widget.js
 * ゲームに貼るだけの「広告（アフィリエイト）導線」ウィジェット。
 *
 * 設計方針（ゆうきさんの前提に合わせてある）:
 *  - 無料・静的のみ。バックエンド不要。Cloudflare Pages にそのまま置ける。
 *  - fetch を使わない → file:// / OneDrive 直開きでも動く。
 *  - スマホ/PWAファースト（タップしやすい大きさ・レスポンシブ）。
 *  - ステマ規制(2023.10〜)対応：必ず「広告」ラベルを表示する（既定ON・消せない）。
 *  - クリック計測は localStorage に簡易記録（無料）。最終的な成果はASP管理画面で見る。
 *
 * 使い方（最小）:
 *   <script src="asp-widget.js"></script>
 *   <script>
 *     AffKit.render({
 *       mount: '#result',           // 差し込み先(セレクタ or 要素)。省略時は body 末尾。
 *       heading: 'この献立にピッタリ🍳',
 *       items: [
 *         { id:'oisix', label:'Oisix お試しセット', desc:'食材が届く。下ごしらえ不要。', url:'https://...?afid=XXXX', badge:'人気' },
 *         { id:'furusato', label:'ふるさと納税で食材ゲット', desc:'実質2000円で返礼品。', url:'https://...?afid=YYYY' },
 *       ],
 *     });
 *   </script>
 */
(function (global) {
  'use strict';

  var STYLE_ID = 'affkit-style';
  var CLICK_KEY = 'affkit_clicks_v1';

  var CSS = [
    '.affkit{font-family:system-ui,-apple-system,"Hiragino Kaku Gothic ProN",sans-serif;',
    'max-width:520px;margin:16px auto;padding:14px;border:1px solid #e6e6e6;border-radius:16px;',
    'background:#fff;box-shadow:0 2px 10px rgba(0,0,0,.06);box-sizing:border-box}',
    '.affkit__pr{display:inline-block;font-size:11px;font-weight:700;color:#8a6d00;',
    'background:#fff4cc;border:1px solid #ffe28a;border-radius:6px;padding:1px 6px;margin-bottom:8px}',
    '.affkit__h{font-size:15px;font-weight:700;margin:2px 0 10px;color:#222}',
    '.affkit__item{display:flex;align-items:center;gap:10px;text-decoration:none;color:inherit;',
    'padding:12px;border:1px solid #eee;border-radius:12px;margin-top:8px;',
    'transition:transform .08s ease,box-shadow .08s ease;-webkit-tap-highlight-color:transparent}',
    '.affkit__item:active{transform:scale(.98)}',
    '.affkit__item:hover{box-shadow:0 2px 8px rgba(0,0,0,.08)}',
    '.affkit__body{flex:1;min-width:0}',
    '.affkit__label{font-size:14px;font-weight:700;color:#1a73e8;display:flex;align-items:center;gap:6px}',
    '.affkit__badge{font-size:10px;font-weight:700;color:#c5221f;background:#fce8e6;border-radius:5px;padding:1px 5px}',
    '.affkit__desc{font-size:12px;color:#666;margin-top:2px;line-height:1.4}',
    '.affkit__arrow{font-size:18px;color:#bbb;flex:none}',
    '.affkit__note{font-size:10px;color:#999;margin-top:10px;text-align:center;line-height:1.5}'
  ].join('');

  function injectStyle() {
    if (document.getElementById(STYLE_ID)) return;
    var el = document.createElement('style');
    el.id = STYLE_ID;
    el.textContent = CSS;
    document.head.appendChild(el);
  }

  function resolveMount(mount) {
    if (!mount) return document.body;
    if (typeof mount === 'string') return document.querySelector(mount) || document.body;
    return mount;
  }

  // クリックを localStorage に貯める（無料の簡易計測）。
  function recordClick(id) {
    try {
      var raw = global.localStorage.getItem(CLICK_KEY);
      var data = raw ? JSON.parse(raw) : {};
      data[id] = (data[id] || 0) + 1;
      global.localStorage.setItem(CLICK_KEY, JSON.stringify(data));
    } catch (e) { /* プライベートモード等は無視 */ }
  }

  function getClicks() {
    try {
      var raw = global.localStorage.getItem(CLICK_KEY);
      return raw ? JSON.parse(raw) : {};
    } catch (e) { return {}; }
  }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  function buildItem(item) {
    var a = el('a', 'affkit__item');
    a.href = item.url || '#';
    a.target = '_blank';
    // rel: アフィリンクの作法（景表法/SEO的にも sponsored を付ける）。
    a.rel = 'sponsored noopener nofollow';

    var body = el('div', 'affkit__body');
    var label = el('div', 'affkit__label');
    label.appendChild(document.createTextNode(item.label || 'おすすめ'));
    if (item.badge) label.appendChild(el('span', 'affkit__badge', item.badge));
    body.appendChild(label);
    if (item.desc) body.appendChild(el('div', 'affkit__desc', item.desc));

    a.appendChild(body);
    a.appendChild(el('div', 'affkit__arrow', '›'));

    a.addEventListener('click', function () {
      recordClick(item.id || item.label || 'unknown');
    });
    return a;
  }

  function render(opts) {
    opts = opts || {};
    if (!opts.items || !opts.items.length) return null;
    injectStyle();

    var box = el('div', 'affkit');
    box.appendChild(el('span', 'affkit__pr', '広告'));            // ← ステマ規制対応・必須
    if (opts.heading) box.appendChild(el('div', 'affkit__h', opts.heading));

    opts.items.forEach(function (item) { box.appendChild(buildItem(item)); });

    box.appendChild(el('div', 'affkit__note',
      opts.note || '※当ウィジェットは広告（アフィリエイトプログラム）を含みます。'));

    resolveMount(opts.mount).appendChild(box);
    return box;
  }

  global.AffKit = { render: render, getClicks: getClicks };
})(window);
