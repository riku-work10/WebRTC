import struct

# RTP固定ヘッダー(RFC 3550): CSRCリストなしの12byte分だけを扱う
#
#  0                   1                   2                   3
#  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
# |V=2|P|X|  CC   |M|     PT      |       sequence number        |
# |                           timestamp                          |
# |           synchronization source (SSRC) identifier           |
#
# V=2:バージョン, P:padding, X:拡張ヘッダー有無, CC:CSRCの数
# M:marker(フレーム末尾など意味付けはPTに依存), PT:payload type(コーデック種別)
HEADER_FORMAT = "!BBHII"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

VERSION = 2

# よく使われるPT(payload type)の例。RFC 3551で静的に割り当てられている番号
PT_PCMU = 0
PT_DYNAMIC = 96  # 96-127は動的割り当て用(VP8/H.264などはここを使う)


def encode(seq: int, timestamp: int, ssrc: int, payload: bytes,
           payload_type: int = PT_DYNAMIC, marker: int = 0) -> bytes:
    byte0 = (VERSION << 6) | (0 << 5) | (0 << 4) | 0  # P=0, X=0, CC=0
    byte1 = (marker << 7) | (payload_type & 0x7F)
    header = struct.pack(HEADER_FORMAT, byte0, byte1, seq, timestamp, ssrc)
    print(f"[encode] header bytes ({len(header)}byte): {header.hex()}")
    print(f"[encode] seq={seq} ts={timestamp} ssrc={ssrc} marker={marker} pt={payload_type}")
    return header + payload


def decode(packet: bytes) -> tuple[int, int, int, int, int, bytes]:
    header = packet[:HEADER_SIZE]
    byte0, byte1, seq, timestamp, ssrc = struct.unpack(HEADER_FORMAT, header)

    version = byte0 >> 6
    marker = byte1 >> 7
    payload_type = byte1 & 0x7F
    payload = packet[HEADER_SIZE:]

    print(f"[decode] header bytes ({len(header)}byte): {header.hex()}")
    print(f"[decode] version={version} marker={marker} pt={payload_type} "
          f"seq={seq} ts={timestamp} ssrc={ssrc} payload={payload!r}")
    return seq, timestamp, ssrc, payload_type, marker, payload
