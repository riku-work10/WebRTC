import socket
import time

from rtp_format import decode

HOST = "127.0.0.1"
PORT = 9003

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))
print(f"RTP receiver listening on {HOST}:{PORT}")

last_seq = None
received = 0
lost = 0
last_recv_time = None

while True:
    packet, addr = sock.recvfrom(2048)
    recv_time = time.time()
    seq, timestamp, ssrc, payload_type, marker, payload = decode(packet)
    received += 1

    if last_seq is not None:
        gap = seq - last_seq - 1
        if gap > 0:
            lost += gap
            print(f"[receiver] パケットロス検出: seq {last_seq}→{seq} の間に{gap}個欠落")
        interval = recv_time - last_recv_time
        print(f"[receiver] 受信間隔={interval*1000:.1f}ms")

    last_seq = seq
    last_recv_time = recv_time

    print(f"[receiver] from {addr}: seq={seq} ts={timestamp} ssrc={ssrc} "
          f"pt={payload_type} marker={marker} payload={payload!r} "
          f"(受信{received}個 / ロス{lost}個)")
