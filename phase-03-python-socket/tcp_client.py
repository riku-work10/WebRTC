import socket
import sys

HOST = "127.0.0.1"
PORT = 9001

message = sys.argv[1] if len(sys.argv) > 1 else "hello"

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
sock.sendall(message.encode())

data = sock.recv(1024)
print(f"received {len(data)} bytes: {data!r}")
sock.close()
