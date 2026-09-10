import os
import struct

# STUNメッセージフォーマット(RFC 5389)
#
#  0                   1                   2                   3
#  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
# |0 0|     STUN Message Type     |         Message Length       |
# |                         Magic Cookie                         |
# |                                                               |
# |                     Transaction ID (96 bit)                  |
# |                                                               |
#
# 先頭2bitは常に0(STUNとRTPなどを1ポートで多重化する時の判別用)。
# Magic Cookieは固定値0x2112A442で、STUNパケットである目印になる。
HEADER_FORMAT = "!HHI12s"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

MAGIC_COOKIE = 0x2112A442

MSG_TYPE_BINDING_REQUEST = 0x0001
MSG_TYPE_BINDING_RESPONSE = 0x0101

ATTR_MAPPED_ADDRESS = 0x0001
ATTR_XOR_MAPPED_ADDRESS = 0x0020

FAMILY_IPV4 = 0x01


def build_binding_request() -> tuple[bytes, bytes]:
    # Transaction IDはこのリクエストとレスポンスを対応付けるためのランダム値(RFC推奨は乱数性の高い値)
    transaction_id = os.urandom(12)
    header = struct.pack(HEADER_FORMAT, MSG_TYPE_BINDING_REQUEST, 0, MAGIC_COOKIE, transaction_id)
    print(f"[stun] Binding Request送信: transaction_id={transaction_id.hex()}")
    return header, transaction_id


def parse_binding_response(packet: bytes, expected_transaction_id: bytes) -> tuple[str, int]:
    msg_type, length, magic_cookie, transaction_id = struct.unpack(HEADER_FORMAT, packet[:HEADER_SIZE])

    if magic_cookie != MAGIC_COOKIE:
        raise ValueError(f"不正なMagic Cookie: {magic_cookie:#x}")
    if transaction_id != expected_transaction_id:
        raise ValueError("Transaction IDが一致しない(別のリクエストへの応答の可能性)")
    if msg_type != MSG_TYPE_BINDING_RESPONSE:
        raise ValueError(f"Binding Response以外を受信: type={msg_type:#x}")

    body = packet[HEADER_SIZE:HEADER_SIZE + length]
    ip, port = None, None

    # 属性(Attribute)はTLV(Type-Length-Value)の並び。1つずつ読み進める
    offset = 0
    while offset < len(body):
        attr_type, attr_len = struct.unpack("!HH", body[offset:offset + 4])
        attr_value = body[offset + 4:offset + 4 + attr_len]

        if attr_type == ATTR_XOR_MAPPED_ADDRESS:
            ip, port = _decode_xor_mapped_address(attr_value, transaction_id)
            print(f"[stun] XOR-MAPPED-ADDRESS: {ip}:{port}")
        elif attr_type == ATTR_MAPPED_ADDRESS:
            ip, port = _decode_mapped_address(attr_value)
            print(f"[stun] MAPPED-ADDRESS(古い実装向け): {ip}:{port}")

        # 属性は4byte境界にpaddingされる
        offset += 4 + attr_len + (-attr_len % 4)

    if ip is None:
        raise ValueError("応答にMAPPED-ADDRESS系の属性が含まれていない")
    return ip, port


def _decode_mapped_address(value: bytes) -> tuple[str, int]:
    _, family, port, addr = struct.unpack("!BBH4s", value)
    if family != FAMILY_IPV4:
        raise ValueError(f"IPv4以外のfamilyは未対応: {family:#x}")
    return format_ipv4(addr), port


def _decode_xor_mapped_address(value: bytes, transaction_id: bytes) -> tuple[str, int]:
    _, family, xport, xaddr = struct.unpack("!BBH4s", value)
    if family != FAMILY_IPV4:
        raise ValueError(f"IPv4以外のfamilyは未対応: {family:#x}")

    # NAT機器の中には、パケット内のIP/PortをそのままNATしようとする実装があるため、
    # STUNではMagic Cookie(とTransaction ID)とXORして「IPアドレスに見えない形」で運ぶ
    magic_cookie_bytes = struct.pack("!I", MAGIC_COOKIE)
    port = xport ^ (MAGIC_COOKIE >> 16)
    addr = bytes(b ^ m for b, m in zip(xaddr, magic_cookie_bytes))
    return format_ipv4(addr), port


def format_ipv4(addr: bytes) -> str:
    return ".".join(str(b) for b in addr)
