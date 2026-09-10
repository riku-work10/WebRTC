import os
import socket
import struct

# Phase 7で作ったSTUN Binding Requestの最小版。
# ICEのsrflx candidate(NAT越しのPublic IP:Port)を得るためだけに使う

MAGIC_COOKIE = 0x2112A442
STUN_SERVER = ("stun.l.google.com", 19302)


def get_srflx_candidate() -> tuple[str, int, int]:
    """STUNサーバーに問い合わせて (public_ip, public_port, local_port) を返す"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(3)

    transaction_id = os.urandom(12)
    request = struct.pack("!HHI12s", 0x0001, 0, MAGIC_COOKIE, transaction_id)
    sock.sendto(request, STUN_SERVER)

    response, _ = sock.recvfrom(2048)
    local_port = sock.getsockname()[1]
    sock.close()

    _, length, _, _ = struct.unpack("!HHI12s", response[:20])
    body = response[20:20 + length]

    offset = 0
    while offset < len(body):
        attr_type, attr_len = struct.unpack("!HH", body[offset:offset + 4])
        value = body[offset + 4:offset + 4 + attr_len]
        if attr_type == 0x0020:  # XOR-MAPPED-ADDRESS
            _, _, xport, xaddr = struct.unpack("!BBH4s", value)
            port = xport ^ (MAGIC_COOKIE >> 16)
            cookie_bytes = struct.pack("!I", MAGIC_COOKIE)
            addr = bytes(b ^ m for b, m in zip(xaddr, cookie_bytes))
            ip = ".".join(str(b) for b in addr)
            return ip, port, local_port
        offset += 4 + attr_len + (-attr_len % 4)

    raise ValueError("XOR-MAPPED-ADDRESSが見つからない")


def get_host_ip() -> str:
    """このPCのPrivate IP(Phase 6と同じ「connectトリック」)"""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
