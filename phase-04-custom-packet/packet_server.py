import socket
from packet_format import encode, decode, TYPE_ACK

HOST = "127.0.0.1"
PORT = 9002

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))
print(f"Packet server listening on {HOST}:{PORT}")

while True:
    packet, addr = sock.recvfrom(1024)
    seq, type_, payload = decode(packet)
    print(f"from {addr}: seq={seq} type={type_} payload={payload!r}")

    ack = encode(seq, TYPE_ACK, b"")
    sock.sendto(ack, addr)
