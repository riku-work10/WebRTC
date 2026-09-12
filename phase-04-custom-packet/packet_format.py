import struct

# !IBHはstructモジュールにヘッダのバイト構造をどうやって組み立てるかを指示するフォーマット文字列です。
# ヘッダー: seq番号(4byte) + type(1byte) + payload長(2byte)
# ! = ネットワークバイトオーダー(ビッグエンディアン)
# I — unsigned int、4byte → seq番号(パケットの連番)
# B — unsigned char、1byte → type(このパケットの種類。DATAかACKか)
# H — unsigned short、2byte → payloadの長さ(何byteのデータが後ろに続くか)
HEADER_FORMAT = "!IBH"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

# 1ならパケットは実データ、２ならACK
TYPE_DATA = 1
TYPE_ACK = 2


def encode(seq: int, type_: int, payload: bytes) -> bytes:
    header = struct.pack(HEADER_FORMAT, seq, type_, len(payload))
    print(f"[encode] header bytes ({len(header)}byte): {header.hex()}")
    print(f"[encode] payload bytes ({len(payload)}byte): {payload!r}")
    return header + payload

def decode(packet: bytes) -> tuple[int, int, bytes]:
    header = packet[:HEADER_SIZE]
    print(f"[decode] header bytes ({len(header)}byte): {header.hex()}")
    seq, type_, payload_len = struct.unpack(HEADER_FORMAT, header)
    payload = packet[HEADER_SIZE:HEADER_SIZE + payload_len]
    print(f"[decode] seq={seq} type={type_} payload_len={payload_len} payload={payload!r}")
    return seq, type_, payload
