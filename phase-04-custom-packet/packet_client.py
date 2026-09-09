import socket
import sys
from packet_format import encode, decode, TYPE_DATA

HOST = "127.0.0.1"
PORT = 9002

message = sys.argv[1] if len(sys.argv) > 1 else "hello"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

seq = 1
packet = encode(seq, TYPE_DATA, message.encode())
sock.sendto(packet, (HOST, PORT))

ack_packet, addr = sock.recvfrom(1024)
ack_seq, ack_type, _ = decode(ack_packet)
print(f"received ACK: seq={ack_seq} type={ack_type} from {addr}")
