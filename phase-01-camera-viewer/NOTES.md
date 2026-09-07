# Phase 1 学習記録: Camera / Microphone Viewer

## コード全体の流れ（[src/main.ts](src/main.ts)）

```
ページ読み込み
   ↓
DOM要素を取得して変数に保持
   ↓
enumerateDevices() でカメラ/マイク一覧を取得
   → 許可前なので label は空、"Camera 0"のような仮名で<select>に表示
   ↓
ユーザーがStartを押す / セレクトを変更する
   ↓
stopCurrentStream() : 前回のtrackがあればstop()して後片付け
   ↓
<select>と<input>の値からconstraints(希望条件)を組み立てる
   ↓
getUserMedia(constraints) : OSに許可を求め、MediaStreamを取得
   ↓
currentStream = stream        (自分の後片付け用の参照)
video.srcObject = stream       (ブラウザに描画させるための参照)
   ↓
enumerateDevices()をもう一度   (今度はlabel付きで<select>を更新)
   ↓
getTracks().map(describeTrack) → JSON.stringify → 画面に表示
```

1つの`MediaStream`への参照を`currentStream`と`video.srcObject`の2箇所に保存しているが、これはコピーではなく「同じ実体を指す2つの目印（参照）」。片方(`video.srcObject`)は画面表示のためブラウザに渡すもの、もう片方(`currentStream`)は自分たちが後で`stop()`するために保持しているもの、と役割が異なる。

## Browser Media APIの要点

```
enumerateDevices()  → 一覧を見るだけ(使用権は得ない)
getUserMedia()      → 実際に使用権を得て、データを流してもらう

deviceId  → サイトごとに加工されたランダムID(追跡防止のため、本物のハードウェアIDではない)
groupId   → 同じ物理ハードウェアに属するデバイス(例: ヘッドセットのマイクとスピーカー)をまとめるID
label     → 許可後にしか見えない製品名(プライバシー保護のため許可前は空文字)
"default" → OSが今選んでいる標準デバイスを指す、Chrome独自の特殊deviceId

exact → 絶対条件。満たせないとgetUserMedia全体がエラー(OverconstrainedError)になる
ideal → 希望条件。満たせなければブラウザが一番近い値で妥協して返す

video.srcObject → URLを持たない"生きたデータ(MediaStream)"をそのまま<video>に渡す仕組み
                  (src=はURL文字列を指定してブラウザに取りに行かせる、srcObjectはオブジェクト参照を直接渡す)

MediaStream と MediaStreamTrack
   → 1つのStreamの中にvideo/audioのtrackが複数入っている
   → track.stop()を呼ばないとカメラ/マイクがOSレベルで解放されないため、
     新しいstreamを取得する前に必ず古いtrackをstopする必要がある
```

## ブラウザ⇄サーバー間の通信

```
Chromeというプロセス と Pythonというプロセスは直接会話できない
   ↓ 必ずOS(カーネル)が仲介する
localhost = 127.0.0.1 = このPC自身を指す特別な住所(/etc/hostsで定義)
   ↓
loopback(lo0)という仮想的な経路で、外に出ずに折り返す
   ↓
Pythonの http.server が "GET /index.html" のようなHTTPリクエストを受け取り
   ファイルを開いて、Content-Type付きでそのまま返す
```

`Content-Type`は拡張子から判定した「申告」に過ぎず（ファイルの中身は見ていない）、ブラウザはこの申告だけを頼りにHTML/CSS/JSとしての扱いを決める。`http.server`の内部（`socketserver.py`）では、実際に`socket()` → `bind()` → `listen()` → `accept()`というOSのAPIが直接呼ばれている。

## キャッシュ

```
①ヒューリスティックキャッシュ
   Cache-Controlヘッダーが無いと、ブラウザが独自判断で
   サーバーに聞きにも行かず保存済みファイルを使い回す(disk cache)
   → これが最初「main.tsを編集してもブラウザに反映されない」原因だった

②条件付きリクエスト(再検証)
   Last-Modified / If-Modified-Since ヘッダーで「変わってる?」とサーバーに聞く
   変わってなければ304 Not Modified(本体なし)、変わっていれば200+本体

Cache-Control: no-cache → 「保存はするが、毎回②で確認してから使う」という意味
Cache-Control: no-store → 「そもそも保存しない」という意味(no-cacheとは別物、紛らわしい)
```

この理解をもとに [serve.py](serve.py) を自作し、`end_headers()`をオーバーライドして`Cache-Control: no-cache`を追加。標準の`python3 -m http.server`を`python3 serve.py`に置き換えることで、開発中の反映漏れ問題を解決した。

## ビルド・パッケージ管理

```
main.ts (型情報あり、人間向け)
   ↓ tsc がコンパイル
   1. 型チェック(ミスがあれば止める。noEmitOnErrorの設定通り)
   2. 型情報(as X, : Type など)を取り除く
dist/main.js (型情報なし、ブラウザが実行できる純粋なJS)

npm install   → registry.npmjs.org から node_modules/ にパッケージをダウンロードする係
npm run build → package.jsonのscriptsを見て、node_modules/.bin/tscを実行するだけ
package-lock.json → 実際にインストールされた正確なバージョンを記録(再現性のため)
```

Pythonの`import http.server`も同じ発想で、`python3`実行ファイルが自分のインストール場所を基準に`sys.path`(標準ライブラリの捜索場所リスト)を起動時に用意しており、そこから`http/server.py`を見つけている。「実行ファイル自身が、自分の付属品(標準ライブラリ)の場所を知っている」という点が共通の仕組み。

## HTTPサーバーの分類

```
①簡易サーバー(開発・学習用)     : Python http.server, Ruby WEBrick, Node.jsのhttpモジュール
②アプリケーションサーバー       : Gunicorn/uWSGI(Python), Puma/Unicorn(Ruby), Node自身(特殊)
③Web/プロキシサーバー          : nginx, Apache (静的配信・SSL終端・負荷分散。アプリコードは実行しない)
```

本番構成は `nginx(③) → Puma等(②) → アプリのコード` という3層になることが多い。どの層でも、一番底では同じ`socket()`→`bind()`→`listen()`→`accept()`というOSのAPIを呼んでいる。

## innerHTML とセキュリティ

```
innerHTML  → 代入した文字列をHTMLタグとして解釈する(柔軟だが、onerror等でJS実行のリスク=XSSがある)
textContent → 代入した文字列をただの文字として扱う(安全、タグとしては効かない)
```

`main.ts`では、ブラウザ自身が生成する信頼できる値(deviceId, label)の表示には`innerHTML`、JSON文字列の表示には`textContent`を使い分けている。ユーザー入力を扱う場面では基本的に`textContent`または適切なエスケープが必要。

## 未消化・今後の課題

- socket / TCP / UDPの詳細な仕組み(Phase 3で自分の手で最小コードを書いてから、改めて理解する予定)
- Video Frameの内部構造(Phase 2)
