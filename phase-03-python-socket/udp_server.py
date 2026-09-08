import socket

HOST = "127.0.0.1"
PORT = 9000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))
print(f"UDP server listening on {HOST}:{PORT}")

while True:
    data, addr = sock.recvfrom(1024)
    print(f"received {len(data)} bytes from {addr}: {data!r}")
    sock.sendto(data, addr)  # 受け取ったものをそのまま送り返す(echo)
