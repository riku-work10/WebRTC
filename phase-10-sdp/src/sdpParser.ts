// SDP(RFC 4566)の各行プレフィックスの意味を注釈する。
// 完全なパーサーではなく、「この行が何を表しているか」を人間向けに説明するだけの簡易版

interface Rule {
  test: (line: string) => boolean;
  describe: (line: string) => string;
}

const rules: Rule[] = [
  { test: (l) => l.startsWith("v="), describe: () => "Protocol Version。SDPの仕様バージョン(常に0)" },
  {
    test: (l) => l.startsWith("o="),
    describe: () => "Origin。セッションの発行者情報(username, session-id, session-version, ネットワーク種別, アドレス)",
  },
  { test: (l) => l.startsWith("s="), describe: () => "Session Name。セッション名(WebRTCでは慣習的に \"-\")" },
  { test: (l) => l.startsWith("t="), describe: () => "Timing。セッションの開始/終了時刻(0 0 = 制限なし)" },
  {
    test: (l) => l.startsWith("a=group:BUNDLE"),
    describe: () => "複数のm=行(音声/映像/データ)を1本のICE/DTLS接続にまとめる(BUNDLE)対象のmid一覧",
  },
  {
    test: (l) => l.startsWith("m="),
    describe: (l) => {
      const [, media, port, proto, ...fmts] = l.split(" ");
      return `Media Description。種別=${media}, port=${port}(SDP単体では使わずICEで決まるダミー値のことが多い), proto=${proto}, payload type一覧=[${fmts.join(", ")}]`;
    },
  },
  { test: (l) => l.startsWith("c="), describe: () => "Connection Information。接続先アドレス(ICE使用時は0.0.0.0のダミーが多い)" },
  { test: (l) => l.startsWith("a=ice-ufrag:"), describe: () => "ICE用の短いユーザー名(candidate生成元の識別・軽い認証に使う)" },
  { test: (l) => l.startsWith("a=ice-pwd:"), describe: () => "ICE用のパスワード(STUNメッセージの整合性チェックに使う共有鍵)" },
  { test: (l) => l.startsWith("a=ice-options:"), describe: () => "ICEの追加オプション(trickle ICE対応の表明など)" },
  {
    test: (l) => l.startsWith("a=fingerprint:"),
    describe: () => "DTLS証明書のフィンガープリント(公開鍵のハッシュ)。Phase 12のDTLSハンドシェイクで、相手の証明書がこれと一致するか検証する",
  },
  {
    test: (l) => l.startsWith("a=setup:"),
    describe: (l) => `DTLSハンドシェイクでどちらが先に鍵交換を始めるか(actpass=どちらでも可, active=自分から, passive=相手を待つ): ${l.split(":")[1]}`,
  },
  { test: (l) => l.startsWith("a=mid:"), describe: (l) => `このm=行のID: "${l.split(":")[1]}"(BUNDLEでどのcandidateがどのメディアか対応付けるのに使う)` },
  { test: (l) => l.startsWith("a=extmap:"), describe: () => "RTPヘッダー拡張の割り当て(音量レベルや送信時刻など、RTP本体以外に載せる追加情報の番号)" },
  { test: (l) => l === "a=sendrecv", describe: () => "このメディアを送信もし、受信もする" },
  { test: (l) => l === "a=recvonly", describe: () => "このメディアは受信のみ(送らない)" },
  { test: (l) => l === "a=sendonly", describe: () => "このメディアは送信のみ(受け取らない)" },
  { test: (l) => l === "a=inactive", describe: () => "このメディアは送受信どちらもしない" },
  { test: (l) => l.startsWith("a=rtcp-mux"), describe: () => "RTPとRTCPを同じポート/コネクションで多重化する(別ポートを使わない)" },
  { test: (l) => l.startsWith("a=rtcp-rsize"), describe: () => "RTCPのReduced-Sizeパケットを許可する" },
  {
    test: (l) => l.startsWith("a=rtpmap:"),
    describe: (l) => {
      const rest = l.slice("a=rtpmap:".length);
      const [pt, codec] = rest.split(" ");
      return `payload type ${pt} をcodec "${codec}" に対応付ける(Phase 5のRTPヘッダーのPTフィールドが指す先)`;
    },
  },
  { test: (l) => l.startsWith("a=rtcp-fb:"), describe: () => "そのcodecでサポートするRTCPフィードバック機能(NACKでの再送要求、PLIでのキーフレーム要求など)" },
  { test: (l) => l.startsWith("a=fmtp:"), describe: () => "codecごとの追加パラメータ(H.264のprofile-level-idなど)" },
  { test: (l) => l.startsWith("a=ssrc:"), describe: () => "このメディアのSSRC(Phase 5のRTPヘッダーにも載る送信元識別子)と、cname等の付随情報" },
  { test: (l) => l.startsWith("a=msid:"), describe: () => "ブラウザのMediaStream/MediaStreamTrackのIDとの対応付け(SDPには本来ない、WebRTC独自の拡張)" },
  {
    test: (l) => l.startsWith("a=candidate:"),
    describe: () => "ICE candidate(Phase 8で自作したものと同じ形式)。host/srflx/relayのアドレス情報",
  },
  { test: (l) => l.startsWith("a="), describe: (l) => `その他の属性(a=): ${l}` },
];

export function annotate(line: string): string {
  const rule = rules.find((r) => r.test(line));
  return rule ? rule.describe(line) : "(未分類の行)";
}
