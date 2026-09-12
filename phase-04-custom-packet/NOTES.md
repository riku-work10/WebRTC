# Phase 4 学習記録: Packetを自作する

## この Phase の目的

Phase 3で生のUDP(`sendto`/`recvfrom`)を触ったが、UDPの1パケットは「ただのbytesの塊」でしかなく、送る側と受ける側で「これは何番目のパケットか」「どんな種類のデータか」「本文は何byteか」を区別する仕組みが元々備わっていない。この Phase では、その区別を自分で決めたバイナリフォーマット(ヘッダー+ペイロード)として設計し、`struct`モジュールでbytesとの相互変換を行う。ここで作った`seq/type/payload長`という構造が、Phase 5(RTP)のヘッダー(`seq/timestamp/SSRC`など)を読み解く土台になる。

## 進数・bit/byteの基礎(このPhaseの前提知識)

混乱しやすいので3つの軸に分けて整理した。

- **軸①: 単位(bit/byte)** — bitは0/1の最小単位。1byte=8bit=256通り。nbitで`2^n`通り表現できる
- **軸②: 進数(2進数/10進数/16進数)** — 同じ値の「見せ方」の違い。実体は常に2進数で、`print()`はデフォルトで10進数、`.hex()`は明示的に16進数に変換して見せているだけ
- **軸③: データ型(str/int/bytes)** — `str`(文字列)と`int`(数値)は別物。`str→bytes`は`.encode()`(文字コード表を引く変換)、`int→bytes`は`struct.pack()`(数値を2進数の箱に詰める変換)で、変換の仕組みが根本的に違う

```python
'1'.encode()        # → b'1' (hex: 31)  ← ASCIIコード表で'1'に49が割り当てられている
struct.pack('!I', 1) # → b'\x00\x00\x00\x01' (hex: 00000001) ← 数値1を4byteの2進数に変換
```

同じ「1」でも経路が違えば全く別のbytesになる、というのがこのPhaseで一番腑に落ちたポイント。

## ヘッダーフォーマットの設計

[packet_format.py](packet_format.py):

```python
HEADER_FORMAT = "!IBH"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

TYPE_DATA = 1
TYPE_ACK = 2
```

| 指定子 | byte数 | bit数 | 表せる範囲 | 使われているフィールド |
|---|---|---|---|---|
| `I` | 4byte | 32bit | 0〜約42億 | seq番号(パケットが増えても余裕を持たせる) |
| `B` | 1byte | 8bit | 0〜255 | type(DATA=1, ACK=2程度で十分) |
| `H` | 2byte | 16bit | 0〜65535 | payload長(UDPの実用上限を考えれば十分) |

`!`はネットワークバイトオーダー(ビッグエンディアン)指定。送受信するマシンによってCPUのエンディアンが違う可能性があるため、バイト列の解釈を一致させる取り決めとして必要。

各フィールドの型は「そのフィールドに入りうる値の最大値」から逆算して選ぶ、というのが設計の考え方。`payload_len`が2byte(上限65535)なので、それを超えるサイズのpayloadを渡すと`struct.pack`が`struct.error: 'H' format requires 0 <= number <= 65535`で例外を出す(実験で確認済み)。実際のプロトコル(RTPなど)は、この上限に対して「フィールドを大きくする」のではなく「大きいデータは複数パケットに分割する」という設計で対応している。

## `struct`の3関数

```python
struct.calcsize(format)        # フォーマットが表す構造の合計byte数を計算するだけ(値は渡さない)
struct.pack(format, v1, v2, …) # Pythonの値(int) → bytes に変換する
struct.unpack(format, bytes)   # bytes → Pythonの値(タプル) に変換する。packの逆
```

`HEADER_SIZE`(`calcsize`の結果)は、受信したbytesの「どこまでがヘッダーか」を切り出す境界値としてそのまま使われる。

## パケットの組み立て/分解

```python
def encode(seq, type_, payload: bytes) -> bytes:
    header = struct.pack(HEADER_FORMAT, seq, type_, len(payload))
    return header + payload   # bytes同士を+で連結するだけ

def decode(packet: bytes):
    header = packet[:HEADER_SIZE]                              # 先頭HEADER_SIZE byteを切り出す
    seq, type_, payload_len = struct.unpack(HEADER_FORMAT, header)
    payload = packet[HEADER_SIZE:HEADER_SIZE + payload_len]     # ヘッダーに書かれた長さ分だけ切り出す
    return seq, type_, payload
```

- `header + payload`は文字列の`+`連結と同じ感覚で、bytes同士をただ前後にくっつけているだけ。連結した時点で「どこまでがheaderか」という区切りの情報は失われる
- だからこそ`decode()`側で「先頭`HEADER_SIZE`byteは必ずheader」という**固定長の約束**を使ってスライスし、ヘッダーに埋め込んだ`payload_len`を頼りにpayloadを正確に切り出す。この「固定長ヘッダー+長さフィールド」という設計が、可変長のpayloadを安全に扱うための仕組みそのもの
- `len(payload)`は`payload`がすでに`bytes`になっている前提で「byte数」を数えている。もし`str`のまま`len()`を呼ぶと「文字数」を数えてしまい、日本語のようなマルチバイト文字(UTF-8で1文字3byte)だと実際のbyte数とズレて壊れる。実験で`"今日はありがとう"`(8文字)が`.encode()`後は24byteになることを確認した

## 実際に動かして確認したログ

`packet_server.py`をバックグラウンドで起動し、`packet_client.py "hello"`を実行:

```
=== client.log ===
[encode] header bytes (7byte): 00000001010005
[encode] payload bytes (5byte): b'hello'
[decode] header bytes (7byte): 00000001020000
[decode] seq=1 type=2 payload_len=0 payload=b''
received ACK: seq=1 type=2 from ('127.0.0.1', 9002)

=== server.log ===
Packet server listening on 127.0.0.1:9002
[decode] header bytes (7byte): 00000001010005
[decode] seq=1 type=1 payload_len=5 payload=b'hello'
from ('127.0.0.1', 58104): seq=1 type=1 payload=b'hello'
[encode] header bytes (7byte): 00000001020000
[encode] payload bytes (0byte): b''
```

- クライアントが`seq=1, type=1(DATA), payload=b'hello'`を送信 → ヘッダー7byte(`00000001010005`)を見ると、seq(4byte)=`00000001`, type(1byte)=`01`, payload長(2byte)=`0005`ときれいに区切って読める
- サーバーは受け取った`seq=1`をそのまま使い、`type=2(ACK)`・payloadなし(`payload_len=0000`)のパケットを送り返している
- クライアントはそのACKを`decode()`して`seq=1 type=2`を確認できている(Phase3のUDP echoと同様、ACKを自作の仕組みとして実装している)

## まとめ: この Phase で得た理解

- UDPの生のbytesには境界情報が無いため、「固定長ヘッダー+長さフィールド」という設計で自分で境界を作る必要がある
- `int→bytes`(`struct.pack`)と`str→bytes`(`.encode()`)は変換の仕組みが全く別物で、両方を理解して初めて`encode()`関数がやっていることが繋がる
- ヘッダーの各フィールドの型は「入りうる値の最大値」から逆算して決める。2byte(65535)のような上限を超えるケースは、フィールド拡大ではなく「分割送信」で対処するのが実プロトコル(RTP)の考え方
- ここで作ったseq/type/payload長というヘッダー構造が、そのままPhase5のRTPヘッダー(seq/timestamp/SSRC)の理解の土台になった

## 未消化・今後の課題

- ヘッダーのbit単位での詰め込み(1byteに複数フィールドを混ぜる、RTPの`V/P/X/CC`のような設計)はPhase5(`rtp_format.py`)で扱った内容で、Phase4の`packet_format.py`自体はフィールドごとにbyteを丸ごと使う設計なので未体験
- 意図的にpayload長を65535超にして`struct.error`が実際に起きる様子を、`packet_client.py`経由で(単体のstruct呼び出しではなく)確認していない
