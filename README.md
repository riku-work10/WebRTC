# WebRTC 学習プロジェクト

フレームワークを使わず、HTML / CSS / TypeScript / Python標準ライブラリ / Browser Web APIだけを使ってWebRTCの仕組みを理解するための学習プロジェクト。

サイクル: 実装させる → コードを読む → 分からない箇所を見つける → 調べる → 小さな実験をする → 理解する → 読み直す → 次へ

## 進捗

- [x] Phase 1: Browser Media API（Camera / Microphone Viewer）— `phase-01-camera-viewer/`
- [x] Phase 2: Video Frameを理解する — `phase-02-video-frame/`
- [x] Phase 3: Python Socket — `phase-03-python-socket/`
- [ ] Phase 4: Packetを自作する
- [ ] Phase 5: RTP / RTCP
- [ ] Phase 6: NAT / UDP / Public IP
- [ ] Phase 7: STUN
- [ ] Phase 8: ICE
- [ ] Phase 9: WebRTC API
- [ ] Phase 10: SDP
- [ ] Phase 11: Signaling
- [ ] Phase 12: DTLS / SRTP
- [ ] Phase 13: Codec
- [ ] Phase 14: WebRTC Statistics
- [ ] Phase 15: Wireshark
- [ ] Phase 16: TURN
- [ ] Phase 17: AWS
- [ ] Phase 18: 最小WebRTCシステム
- [ ] Phase 19: 最後にWebアプリ化

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
```

各フェーズは `phase-XX-名前/` ディレクトリごとに独立しており、`tsconfig.json`は共通の`tsconfig.base.json`を継承している。`serve.py`は標準の`http.server`に`Cache-Control: no-cache`を追加した自作の簡易サーバー（詳細は各フェーズの`NOTES.md`を参照）。

## 方針

- 最初はフレームワーク（Nuxt / Next.js / React / Rails / Express / FastAPI / Socket.IO / WebRTC専用ライブラリ）を使わない
- TypeScriptはBrowser側（Camera / Microphone / MediaStream / RTCPeerConnection / SDP / WebSocketなど）を担当
- Pythonは標準ライブラリのみでSocket / TCP / UDP / STUN / Signalingなどを担当
- 各フェーズは「最小コード → 実行 → 観察 → 変更 → 再実行」で進める
- コードを読んでから疑問点を掘り下げる。答えを先に大量に与えない
- 動作確認・検証のたびに、必要になったLinuxコマンドをその場で学ぶ（一覧は[LINUX_COMMANDS.md](LINUX_COMMANDS.md)）
