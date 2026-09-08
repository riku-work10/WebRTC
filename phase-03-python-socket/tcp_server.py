import socket

HOST = "127.0.0.1"
PORT = 9001

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen()
print(f"TCP server listening on {HOST}:{PORT}")

while True:
    conn, addr = sock.accept()
    print(f"connected by {addr}")
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(f"received {len(data)} bytes: {data!r}")
            conn.sendall(data)  # 受け取ったものをそのまま送り返す(echo)
    print(f"connection with {addr} closed")
