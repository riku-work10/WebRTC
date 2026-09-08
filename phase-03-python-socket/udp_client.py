import socket
import sys

HOST = "127.0.0.1"
PORT = 9000

message = sys.argv[1] if len(sys.argv) > 1 else "hello"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(message.encode(), (HOST, PORT))

data, addr = sock.recvfrom(1024)
print(f"received {len(data)} bytes from {addr}: {data!r}")
