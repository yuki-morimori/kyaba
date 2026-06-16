# 同梱パッケージの作り方（販売者＝あなた向け）

買い手に **「Pythonインストール不要・.batを押すだけ」** で渡すための、
Python同梱パッケージを作る手順です。EXE化はしません（.batのまま）。

## 仕組み（なぜPython不要になるか）
Windowsの「埋め込み版Python」を商品フォルダに同梱します。
買い手のPCにPythonが無くても、同梱したPythonで動きます。

```
買い手の体験:
  zipを解凍 → 「出品スタート.bat」をダブルクリック → メニューを選ぶだけ
  （Pythonのインストールも、コマンド入力も一切不要）
```

## 販売者がやること（1回だけ・Windowsで）
> ⚠️ この組み立てだけは **Windows** が必要です（埋め込み版PythonがWindows用のため）。
> Mac/Linuxしか無い場合は、Windows PCかクラウドのWindowsを一時的に使ってください。

1. このリポジトリ（`auto_publisher` を含む）をWindowsに置く
2. PowerShell を開き、`auto_publisher` フォルダで実行:
   ```powershell
   powershell -ExecutionPolicy Bypass -File packaging\build_windows.ps1
   ```
3. `products\dist\自動出品ツール_win.zip` が完成
4. それを **そのまま販売ページ（BOOTH等）にアップロード**

### Chromeを持っていない買い手にも対応したい場合
標準ではPCのChromeを使います（ほとんどの人が持っている）。
Chrome未所持の人にも確実に動かしたいなら、Chromiumも同梱:
```powershell
powershell -ExecutionPolicy Bypass -File packaging\build_windows.ps1 -BundleChromium
```
※サイズが約150MB増えます。

## 完成パッケージの中身（買い手が受け取るもの）
```
自動出品ツール/
├── 出品スタート.bat     ← 買い手はこれを押すだけ
├── 設定.yaml            ← 出品先の設定（BOOTH用を初期同梱）
├── 商品リスト.csv        ← 出品したい商品を書く
├── 説明書.md            ← 使い方
├── python/              ← 同梱Python（インストール不要）
└── app/                 ← ツール本体
```

## 動作確認（販売前に必ず）
作ったzipを **別フォルダ（できれば別PC）で解凍**し、
`出品スタート.bat` → 「1) 下見」で入力内容が表示されればOK。
「2) 確認」でブラウザが開き、ログイン後に自動入力されれば本番準備完了です。

## 売り方メモ
- これで「Python不要」になったので、商品説明の動作環境を
  **「Windows・インストール不要・ダブルクリックで起動」** に更新できます
  （`products/sales_copy.md` の商品3を書き換え）。
- このエンジンは**フォームを自動入力するだけ**なので、出品以外にも応用可。
  設定ファイルを変えれば「○○への自動記入ツール」として別商品にもできます。

## 注意
- 本パッケージの利用・配布は各サイト規約・法令の範囲で。
- 出品先サイトの仕様変更で動かなくなることがあります（`設定.yaml`のセレクタ調整で対応）。
