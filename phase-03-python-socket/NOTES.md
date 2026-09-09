# Phase 3 学習記録: Python Socket

## この Phase の目的

WebRTCは最終的にUDPの上にRTP/ICE/DTLSなどを自前で積んでいく技術。Phase 9でブラウザの`RTCPeerConnection`(下回りを全部隠してくれるAPI)を使う前に、「ソケットとは何か」「TCPとUDPは何がどう違うのか」を`socket`モジュールで最小コードを書いて体感する。

## import しているものの正体

```
import socket → OSのソケットAPI(socket()/bind()/sendto()/recvfrom()など、Cのシステムコールとほぼ1対1)を
                 Pythonから呼べるようにするラッパー。実体は
                 /Library/Frameworks/Python.framework/Versions/3.14/lib/python3.14/socket.py
                 (python3 -c "import socket; print(socket.__file__)" で確認できる)

import sys    → 「今動いているPythonインタプリタ自身」に関する情報を扱うモジュール。
                 .pyファイルとして存在せず、python3という実行ファイル自体に埋め込まれている
                 (python3自体はCで書かれてコンパイルされた実行ファイル。.pyファイルを読んで実行する側)
                 sys.argv → コマンドライン引数のリスト。sys.argv[0]がスクリプト名、[1]以降が引数
```

## ソケットとは何か(Pythonを抜きにした一般論)

ソケットはOS(カーネル)が提供する「通信の窓口」という抽象概念。ファイルディスクリプタ(番号札)として管理され、`open()`でファイルを開くのと似た扱い(`phase-01`のNOTES.mdで見た「HTTPサーバーも同じsocket()→bind()→listen()→accept()を呼んでいる」という話と同じ土台)。

```
socket()   → 窓口を1つ用意する
bind()     → その窓口に「自分の住所(IPアドレス+ポート番号)」を割り当てる
listen()   → (TCPのみ)接続を受け付ける状態にする宣言
accept()   → (TCPのみ)誰かが接続してくるのを待ち、専用の通信路を1本作る
connect()  → (TCPのみ、クライアント側)相手の窓口に接続を要求する
send/recv        → 接続済みの通信路に対して送受信する
sendto/recvfrom  → 接続なしで、毎回相手の住所を指定して送受信する
close()    → 窓口を閉じる
```

IPアドレスは「どのマシン宛か」、ポート番号は「同じマシンの中でどのプログラム宛か」を区別するもの。この2つの組み合わせがネットワーク上で1つの窓口を一意に指す。

## UDP: コネクションレス

[udp_server.py](udp_server.py) / [udp_client.py](udp_client.py)で確認した通り:

```python
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # AF_INET=IPv4, SOCK_DGRAM=UDP
sock.bind((HOST, PORT))          # bindした瞬間にもう受信可能。listen/acceptは不要
...
data, addr = sock.recvfrom(1024) # 受信のたびに「誰から来たか」を毎回受け取る
sock.sendto(data, addr)          # 送るたびに宛先を毎回明示的に指定する
```

UDPは「事前に握手(接続確立)をせず、いきなりデータの塊(データグラム)を送りつける」方式。届くかどうか・順番通りに届くかは保証されない代わりに、オーバーヘッドが少なく速い。`netstat`で見ても`LISTEN`/`ESTABLISHED`のような「状態」が一切出ない(接続という実体が無いため)。

### なぜサーバーは受け取るだけでなく送り返す(echo)のか

- UDPには「届いたかどうか」を教えてくれる仕組み(ACK)がプロトコルレベルで無いため、届いたことを確認する手段をアプリ側(このコード)で自作する必要がある。一番単純な確認方法が「受け取ったものをそのまま送り返す」こと
- `udp_client.py`は送信後に`recvfrom()`で応答を待つ作りになっているため、サーバーが送り返さないとクライアント側がそこで永遠にハングする(サーバー未起動のままクライアントを動かすと同じ理由でハングすることも確認した)
- 1つのスクリプトで送信(`sendto`)と受信(`recvfrom`)の両方のAPIを、送る側・受け取る側の立場から確認できる、という学習上の狙いもある

### クライアント側ポートが毎回変わる理由(実験で確認)

```
python3 udp_client.py "hi"   # 1回目 → サーバーログ: from ('127.0.0.1', 51915)
python3 udp_client.py "hi"   # 2回目 → from ('127.0.0.1', 57893)
python3 udp_client.py "hi"   # 3回目 → from ('127.0.0.1', 60669)
```

`udp_client.py`は`bind()`を呼んでいない。`bind()`せずに`sendto()`すると、OSが送信元ポートとして空いているポートを自動でランダムに割り当てる(エフェメラルポート)。実行するたびに新しいプロセス・新しいソケットが作られるので、毎回違うポートが選ばれる。一方サーバー側は`bind((HOST, 9000))`で明示的に固定しているので、クライアントから見て常に9000番に見える(「お店の電話番号(サーバー、固定)」と「かける側の携帯電話(クライアント、毎回変わってもいい)」の関係に近い)。

## TCP: コネクション型

[tcp_server.py](tcp_server.py) / [tcp_client.py](tcp_client.py)で確認した通り:

```python
# サーバー側
sock.bind((HOST, PORT))
sock.listen()
conn, addr = sock.accept()   # ← 接続ごとに専用の通信路(conn)が新規に作られる
with conn:
    data = conn.recv(1024)   # ← addrを指定しなくていい(connが相手と紐付いているため)
    conn.sendall(data)

# クライアント側
sock.connect((HOST, PORT))   # ← 送る前に接続を確立する(3ウェイハンドシェイク)
sock.sendall(message.encode())
```

実際に3回`tcp_client.py`を実行して観察したログ:

```
connected by ('127.0.0.1', 51520)
received 3 bytes: b'hi1'
connection with ('127.0.0.1', 51520) closed
connected by ('127.0.0.1', 51521)
received 3 bytes: b'hi2'
connection with ('127.0.0.1', 51521) closed
connected by ('127.0.0.1', 51522)
received 3 bytes: b'hi3'
connection with ('127.0.0.1', 51522) closed
```

`lsof -iTCP:9001`で確認すると、`sock`(待ち受け窓口)は3回のやり取りの間ずっと`LISTEN`のまま1つだけで、`accept()`のたびに新しい`conn`が作られては閉じられている、という構造がログからも裏付けられた。

### UDPとの対比表

| | UDP | TCP |
|---|---|---|
| クライアント側ポート | 毎回ランダム(bindしないため) | 毎回ランダム(bindしないため。ここは同じ) |
| サーバー側の窓口 | 1つの`sock`が全員分を直接処理 | `sock`は待受専用、`accept()`が相手ごとに`conn`を新規作成 |
| 送受信前の準備 | 不要(いきなり送れる) | `connect()`によるハンドシェイクが必要 |
| 宛先の指定 | 毎回`addr`を指定 | 不要(`conn`自体が相手と紐付いている) |
| 終了 | 概念なし | `close`という明示的なイベントがある |
| `netstat`での見え方 | 状態が出ない | `LISTEN`/`ESTABLISHED`などの状態が見える |

### パケットレベルのハンドシェイク(要sudo、未実施)

`sudo tcpdump -i lo0 -n port 9001`でパケットを覗くと、データが流れる前に以下がやり取りされているはず:

```
Flags [S]   → SYN (接続したい)
Flags [S.]  → SYN-ACK (いいよ、こちらもSYN)
Flags [.]   → ACK (了解)
Flags [P.]  → PUSH+ACK (実際のデータ)
Flags [F.]  → FIN (切断)
```

これが「3ウェイハンドシェイク」の中身。`sudo`のパスワード入力が必要でこのセッションでは未実施(BPFデバイスへのアクセス権限が無いため`Permission denied`)。Phase 15(Wireshark)で本腰を入れて確認する予定。UDPで同じことをすると、SYN/ACKは一切出ず、いきなりデータ本体だけが流れることになるはず。

## プロセス・ポートの確認コマンド(このPhaseで使ったもの)

```bash
lsof -iTCP:PORT -sTCP:LISTEN     # 特定ポートを使っているTCPプロセスを確認(状態も見れる)
lsof -iUDP:PORT                  # 特定ポートを使っているUDPプロセスを確認(状態は無い)
lsof -tiUDP:PORT                 # PIDだけ欲しい時(terse)。killに渡すのに便利
lsof -i -P -n                    # マシン全体のネットワーク接続を一覧
ps -p PID -o pid,ppid,%cpu,etime,command   # 特定プロセスの詳細・経過時間
netstat -an | grep PORT          # TCPは状態あり、UDPは状態なしという違いがここでも見える
```

`python3 udp_server.py &`のように`&`を付けてバックグラウンド実行すると、同じターミナルでサーバーを動かしたまま続けてクライアントを実行できる([linux-shell/10](../linux-shell/10-process-job-control/NOTES.md)のジョブ制御の話そのもの)。

## まとめ: この Phase で得た理解

- WebRTCがUDPを土台に選ぶ理由(信頼性より低遅延を優先。1秒前の映像フレームが再送されても意味が無い)を、TCP/UDPのAPI構造の違いから体感できた
- 「TCPはコネクション確立の手順(`listen`/`accept`/`connect`)がAPIレベルで明確に存在し、UDPには存在しない」という違いを、コードレベルで確認できればこのPhaseの目的としては十分(パケットキャプチャでの検証はPhase 15への持ち越し)
- 次のPhase 4(Packetを自作する)・Phase 5(RTP/RTCP)は、ここで触った`socket.SOCK_DGRAM`(UDP)の上に、自分たちで必要な機能(順序管理・信頼性など)だけを積み増していく作業になる

## 未消化・今後の課題

- `sudo tcpdump`によるパケットレベルでのハンドシェイク確認(Phase 15で本格的に扱う)
- 複数クライアントをほぼ同時に投げた時の挙動(UDPは1つの窓口で順に捌ける、TCPは`accept()`が1つの接続処理を終えるまで次に進めない、という違いの詳細確認)
- クライアント側で`bind()`を明示的に呼んでポートを固定した場合の挙動
