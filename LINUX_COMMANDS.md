# Linuxコマンド学習メモ（フェーズ対応表）

各フェーズの「動作確認・検証」のタイミングで、必要になったコマンドをその都度実際に使いながら覚えていく方針。新しいコマンドを使ったら、このファイルに追記していく。

補足: 開発機はmacOSなので、コマンドによっては本家Linuxと微妙に挙動やオプションが異なる場合がある（例: `netstat`はLinuxでは非推奨になりつつあり`ss`が主流、macOSには`ss`が無い）。将来AWSのLinuxサーバー(Phase 17)に触る際に、この差分にも触れる。

## Phase 1: Browser Media API / HTTPサーバー

| コマンド | 何を確認したか |
|---|---|
| `lsof -iTCP:PORT -sTCP:LISTEN` | 指定ポートで待ち受けているプロセスを確認する |
| `ifconfig lo0` | loopback(ループバック)インターフェースの実体を確認する |
| `cat /etc/hosts` | `localhost`が`127.0.0.1`に対応付けられていることを確認する |
| `which python3` / `which npm` | コマンドの実行ファイルの実体がディスク上のどこにあるかを確認する |
| `grep -n "パターン" ファイル` | ソースコードの中から特定の文字列(関数名など)を検索する |

## Phase 3: Python Socket

| コマンド | 何を確認したか |
|---|---|
| `netstat -an \| grep PORT` | 指定ポートの通信状態(LISTENなど)を一覧で確認する。UDPには"状態"が無いことも確認した |
| `nc -u -w1 HOST PORT` | 自作クライアントを使わず、UDPサーバーに直接データを送る |
| `nc -w1 HOST PORT` | 自作クライアントを使わず、TCPサーバーに直接データを送る |

### 今後試す予定

- `tcpdump -i lo0 udp port 9000` : UDP通信を実際のパケットレベルでキャプチャして観察する(Phase 15 Wiresharkの前哨戦)
- `ss` : Linux環境ではnetstatの代替として使われる(macOSには無い)

## Phase 6: NAT / UDP / Public IP（予定）

- `ifconfig` / `ip addr` : ネットワークインターフェースとPrivate IPを確認する
- `traceroute` : 自分のPCから相手までの経路(ルーター)を確認する
- `curl ifconfig.me` のような外部サービス経由でPublic IPを確認する

## Phase 11: Signaling（予定）

- `ps aux \| grep python` : 動いているPythonプロセスを一覧確認する
- `kill PID` : 特定のプロセスを終了させる
- `tail -f ログファイル` : ログファイルをリアルタイムで監視する

## Phase 15: Wireshark（予定）

- `tcpdump -i any -w capture.pcap` : パケットをファイルに保存し、Wiresharkで開いて詳しく解析する

## Phase 17: AWS（予定）

- `ssh` : リモートのLinuxサーバーに接続する
- `systemctl` : Linuxサーバー上でサービスを管理する
- macOSとLinuxのコマンドの差分に本格的に触れることになる想定
