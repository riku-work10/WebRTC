# WebRTC 学習プロジェクト

フレームワークを使わず、HTML / CSS / TypeScript / Python標準ライブラリ / Browser Web APIだけを使ってWebRTCの仕組みを理解するための学習プロジェクト。

サイクル: 実装させる → コードを読む → 分からない箇所を見つける → 調べる → 小さな実験をする → 理解する → 読み直す → 次へ

## 進捗

- [x] Phase 1: Browser Media API（Camera / Microphone Viewer）— `phase-01-camera-viewer/`
- [ ] Phase 2: Video Frameを理解する
- [ ] Phase 3: Python Socket
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

## 実行方法（Phase 1）

```bash
npm install       # tsc(TypeScriptコンパイラ)のみをインストール
npm run build      # phase-01-camera-viewer/src/main.ts を dist/main.js にコンパイル
cd phase-01-camera-viewer
python3 -m http.server 8000
# ブラウザで http://localhost:8000 を開く
```

## 方針

- 最初はフレームワーク（Nuxt / Next.js / React / Rails / Express / FastAPI / Socket.IO / WebRTC専用ライブラリ）を使わない
- TypeScriptはBrowser側（Camera / Microphone / MediaStream / RTCPeerConnection / SDP / WebSocketなど）を担当
- Pythonは標準ライブラリのみでSocket / TCP / UDP / STUN / Signalingなどを担当
- 各フェーズは「最小コード → 実行 → 観察 → 変更 → 再実行」で進める
- コードを読んでから疑問点を掘り下げる。答えを先に大量に与えない
