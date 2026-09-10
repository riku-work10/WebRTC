# WebRTC 学習プロジェクト

フレームワークを使わず、HTML / CSS / TypeScript / Python標準ライブラリ / Browser Web APIだけを使ってWebRTCの仕組みを理解するための学習プロジェクト。

サイクル: 実装させる → コードを読む → 分からない箇所を見つける → 調べる → 小さな実験をする → 理解する → 読み直す → 次へ

## 進捗

各フェーズの目的・学習手順。実装済みのフェーズは実際にやったこと、未着手のフェーズは着手時の計画として記載する。

### Phase 1: Browser Media API（Camera / Microphone Viewer）✅ — `phase-01-camera-viewer/`
- 目的: ブラウザのMediaDevices系APIでカメラ・マイクを取得し、Streamの構造を理解する
- 学習手順:
  1. `enumerateDevices`でデバイス一覧を取得し`<select>`に表示する
  2. `getUserMedia`で映像/音声を取得し`<video>`に表示する
  3. `deviceId`・constraints(`ideal`/`exact`)を変えて解像度・FPS・デバイスを切り替える
  4. `MediaStreamTrack`の`getSettings`/`getCapabilities`を表示し構造を理解する

### Phase 2: Video Frameを理解する ✅ — `phase-02-video-frame/`
- 目的: 動画が連続した静止画(フレーム)であることをCanvasで体感する
- 学習手順:
  1. `<video>`から`<canvas>`へ`drawImage`で1フレームずつ描画する
  2. `requestAnimationFrame`での描画ループとFPS計測を実装する
  3. `getImageData`/`putImageData`でピクセル単位のデータ(RGBA)を操作する(グレースケール変換)
  4. クリック位置のピクセル値取得を通じて`getBoundingClientRect`による座標変換を理解する

### Phase 3: Python Socket ✅ — `phase-03-python-socket/`
- 目的: OSのsocket APIを直接使い、TCP/UDPの違いをコードの形の違いとして体感する
- 学習手順:
  1. UDPのecho server/clientを`sendto`/`recvfrom`で実装する
  2. TCPのecho server/clientを`bind`/`listen`/`accept`/`connect`で実装する
  3. `netstat`/`lsof`/`nc`で実際のポートと通信を観察する
  4. UDPとTCPのコード構造の違い(コネクションレス/コネクション型)を比較する

### Phase 4: Packetを自作する ✅ — `phase-04-custom-packet/`
- 目的: UDPの上に自分で決めたバイナリフォーマット(ヘッダー+ペイロード)を乗せ、`struct`でのバイナリ操作とヘッダー設計の考え方を理解する。Phase 5(RTP)のヘッダー構造を読むための前段
- 学習手順:
  1. `struct.pack`/`unpack`でヘッダー(seq番号・type・payload長)を組み立て/解析する
  2. UDPでカスタムパケットを送受信し、受信側でヘッダーとペイロードを分離する
  3. ACKパケットを送り返す仕組みを作り、シーケンス番号のやり取りを観察する
  4. ネットワークバイトオーダー(ビッグエンディアン)がなぜ必要かを調べる

### Phase 5: RTP / RTCP — `phase-05-rtp-rtcp/`
- 目的: 実際の音声/映像伝送プロトコルRTPのヘッダー構造を読み、なぜUDPの上に自作パケット(Phase 4)のような仕組みが必要なのかを理解する
- 学習手順:
  1. RTPヘッダーの各フィールド(seq番号・timestamp・SSRCなど)を仕様書ベースで確認する
  2. Phase 4のパケットフォーマットをRTPヘッダーに近づけて自作する
  3. RTCPが何のための制御チャンネルかを調べる(統計・同期)

### Phase 6: NAT / UDP / Public IP ✅ — `phase-06-nat-public-ip/`
- 目的: 自分のPCがPrivate IPを持ち、NATを介してPublic IPに変換される仕組みを体感する
- 学習手順:
  1. `ifconfig`/`ip addr`でPrivate IPを確認する
  2. 外部サービス経由でPublic IPを確認する
  3. `traceroute`で自分から相手までの経路(ルーター)を確認する
  4. NATがポート番号をどう書き換えるかを調べる

### Phase 7: STUN
- 目的: NAT越しに自分のPublic IP/Portを知る仕組み(STUN)を最小実装で理解する
- 学習手順:
  1. STUNプロトコルのメッセージフォーマットを調べる
  2. 自作UDPクライアントから公開STUNサーバーにリクエストを送り、返ってきたPublic IP/Portを確認する
  3. NAT越えがなぜこれだけでは不十分な場合があるか(NATの種類)を調べる

### Phase 8: ICE
- 目的: STUN/TURNの結果を使い、実際に通信可能な経路を選ぶICEの考え方を理解する
- 学習手順:
  1. ICE candidate(host/srflx/relay)の種類を調べる
  2. 複数candidateの中から接続性チェックで経路を選ぶ流れを追う

### Phase 9: WebRTC API
- 目的: ここまでの下位層知識を踏まえて、ブラウザの`RTCPeerConnection`が何を隠蔽しているかを理解する
- 学習手順:
  1. `RTCPeerConnection`を最小構成で使い、Phase 1のMediaStreamを流してみる
  2. 内部でICE/DTLS/SRTPがどう呼ばれているかをログで追う

### Phase 10: SDP
- 目的: 2者間で通信条件(コーデック・ポート・candidateなど)を合意するためのテキスト形式SDPを読めるようにする
- 学習手順:
  1. `createOffer`/`createAnswer`で生成されたSDPを実際に出力して読む
  2. 各行(m=, a=など)が何を意味するか調べる

### Phase 11: Signaling
- 目的: SDP/candidateを交換するためのシグナリングサーバーを自作し、WebRTC自体には仲介の仕組みが無いことを理解する
- 学習手順:
  1. Python標準ライブラリのみでシンプルなシグナリングサーバー(WebSocketまたはHTTP polling)を実装する
  2. `ps aux`/`kill`/`tail -f`でプロセスとログを監視しながらデバッグする

### Phase 12: DTLS / SRTP
- 目的: WebRTCの通信が暗号化される仕組み(DTLSでの鍵交換、SRTPでのメディア暗号化)を理解する
- 学習手順:
  1. DTLSハンドシェイクの流れを調べる
  2. SRTPがRTPペイロードをどう暗号化するかを調べる

### Phase 13: Codec
- 目的: 映像/音声データが圧縮される仕組み(コーデック)の役割を理解する
- 学習手順:
  1. 生のフレームデータ量とエンコード後のデータ量を比較する
  2. VP8/H.264やOpusなど代表的なコーデックの役割の違いを調べる

### Phase 14: WebRTC Statistics
- 目的: `getStats()`を使い、実際の通信品質(パケットロス・遅延・ジッタ)を観察する
- 学習手順:
  1. `RTCPeerConnection.getStats()`の結果を表示する
  2. 意図的に負荷をかけて数値の変化を観察する

### Phase 15: Wireshark
- 目的: ここまで扱ってきたUDP/RTP/STUN/DTLSの通信を実際のパケットキャプチャで目視確認する
- 学習手順:
  1. `tcpdump -i any -w capture.pcap`でパケットを保存する
  2. Wiresharkで開き、Phase 4〜7で学んだヘッダー構造が実際のバイト列と一致することを確認する

### Phase 16: TURN
- 目的: STUNでは越えられないNAT環境で、通信を中継するTURNサーバーの役割を理解する
- 学習手順:
  1. TURNのAllocate/Permission/Channelの流れを調べる
  2. STUNのみの場合とTURN併用時のcandidate選択の違いを比較する

### Phase 17: AWS
- 目的: リモートのLinuxサーバー上でシグナリングサーバーやTURNサーバーを動かし、実運用に近い環境を体験する
- 学習手順:
  1. `ssh`でAWSのLinuxサーバーに接続する
  2. `systemctl`でサービスを起動・管理する
  3. macOSとLinuxのコマンドの差分に触れる

### Phase 18: 最小WebRTCシステム
- 目的: これまでの要素(シグナリング・ICE・SDP・RTP)を組み合わせ、最小構成の1対1通話を動かす
- 学習手順:
  1. 自作シグナリングサーバー経由でofferとanswerを交換する
  2. 実際に映像/音声が届くことを確認する

### Phase 19: 最後にWebアプリ化
- 目的: 学習用の最小実装を、実際に使えるWebアプリの形に整える
- 学習手順:
  1. UI/UXを整える
  2. 複数人通話やエラーハンドリングなど、学習目的では省いていた部分を必要に応じて追加する

## 実行方法

```bash
npm install         # tsc(TypeScriptコンパイラ)のみをインストール(最初の1回だけ)

# Phase 1: Camera / Microphone Viewer
npm run build:phase1
cd phase-01-camera-viewer && python3 serve.py
# ブラウザで http://localhost:8080 を開く

# Phase 2: Video Frame
npm run build:phase2
cd phase-02-video-frame && python3 serve.py
# ブラウザで http://localhost:8081 を開く

# 全フェーズまとめてビルドしたい場合
npm run build

# Phase 3: Python Socket (ビルド不要、標準ライブラリのみ)
cd phase-03-python-socket
python3 udp_server.py &      # ターミナル1
python3 udp_client.py "hi"   # ターミナル2

python3 tcp_server.py &      # ターミナル1
python3 tcp_client.py "hi"   # ターミナル2

# Phase 4: Packetを自作する (ビルド不要、標準ライブラリのみ)
cd phase-04-custom-packet
python3 packet_server.py &      # ターミナル1
python3 packet_client.py "hi"   # ターミナル2

# Phase 5: RTP / RTCP (ビルド不要、標準ライブラリのみ)
cd phase-05-rtp-rtcp
python3 rtp_receiver.py &         # ターミナル1
python3 rtp_sender.py 10          # ターミナル2 (引数は送信フレーム数、省略時10)

# Phase 6: NAT / UDP / Public IP (ビルド不要、標準ライブラリのみ)
cd phase-06-nat-public-ip
python3 check_ip.py
# 加えて `ifconfig`(mac)/`ip addr`(Linux)、`traceroute <宛先>` を手元で実行して比較する
```

各フェーズは `phase-XX-名前/` ディレクトリごとに独立しており、`tsconfig.json`は共通の`tsconfig.base.json`を継承している。`serve.py`は標準の`http.server`に`Cache-Control: no-cache`を追加した自作の簡易サーバー（詳細は各フェーズの`NOTES.md`を参照）。

## 方針

- 最初はフレームワーク（Nuxt / Next.js / React / Rails / Express / FastAPI / Socket.IO / WebRTC専用ライブラリ）を使わない
- TypeScriptはBrowser側（Camera / Microphone / MediaStream / RTCPeerConnection / SDP / WebSocketなど）を担当
- Pythonは標準ライブラリのみでSocket / TCP / UDP / STUN / Signalingなどを担当
- 各フェーズは「最小コード → 実行 → 観察 → 変更 → 再実行」で進める
- コードを読んでから疑問点を掘り下げる。答えを先に大量に与えない
- 動作確認・検証のたびに、必要になったLinuxコマンドをその場で学ぶ（一覧は[LINUX_COMMANDS.md](LINUX_COMMANDS.md)）
