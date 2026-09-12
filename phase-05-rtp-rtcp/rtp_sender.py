import random
import socket
import sys
import time

from rtp_format import encode, PT_DYNAMIC

HOST = "127.0.0.1"
PORT = 9003

CLOCK_RATE = 90000  # 90kHzクロック(映像でよく使われる値)。1フレーム=CLOCK_RATE/fps ずつ進む
FPS = 30
FRAME_INTERVAL_TS = CLOCK_RATE // FPS

frame_count = int(sys.argv[1]) if len(sys.argv) > 1 else 10

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

ssrc = random.randint(0, 2**32 - 1)  # このセッションを識別するID。送信開始時に1回だけ決める
seq = 0
timestamp = 0

print(f"[sender] ssrc={ssrc} を使って{frame_count}フレーム送信します")

for i in range(frame_count):
    fは文字列にしている
    payload = f"frame-{i}".encode()
    marker = 1  # 1フレーム=1パケットなので毎回フレーム末尾扱い
    packet = encode(seq, timestamp, ssrc, payload, payload_type=PT_DYNAMIC, marker=marker)
    sock.sendto(packet, (HOST, PORT))

    seq += 1
    timestamp += FRAME_INTERVAL_TS
    time.sleep(1 / FPS)

print("[sender] 送信完了")
