import socket

HOST = "127.0.0.1"
PORT = 9000


# socket.AF_INETはIPv4を使うことを意味します。AF=アドレスファミリー
# socket.SOCK_DGRAMはUDPを使うことを意味します。
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# OSに対して、指定したIPアドレスとポート番号で待ち受けるように指示
sock.bind((HOST, PORT))
print(f"UDP server listening on {HOST}:{PORT}")

# while Trueは無限ループを意味します。つまり、サーバーは永遠にクライアントからのメッセージを待ち受け続けます。
while True:
    # このデータの展開の仕方をアンパックという
    # dataは受信したデータ、addrは送信元のアドレス情報(IPアドレスとポート番号)が入る
    # 1024は受信するデータの最大バイト数を指定しています。1024バイトを超えるデータは切り捨てられます。
    # recvfromはUDPの受信に使われるメソッド
    # sendtoはUDPの送信に使われるメソッド
    data, addr = sock.recvfrom(1024)
    print(f"received {len(data)} bytes from {addr}: {data!r}")
    sock.sendto(data, addr)  # 受け取ったものをそのまま送り返す(echo)
