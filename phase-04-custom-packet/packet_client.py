import socket
import sys
from packet_format import encode, decode, TYPE_DATA

HOST = "127.0.0.1"
PORT = 9002

message = sys.argv[1] if len(sys.argv) > 1 else "hello"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

seq = 1
# message.encode()は、Pythonの文字列をバイト列に変換するメソッドです。UDPパケットを送信する際には、送信するデータはバイト列である必要があるため、文字列をバイト列に変換するために使用されます。
# sendto()でわたせるのはバイト列だけなので全部それに変換しているだけ！
packet = encode(seq, TYPE_DATA, message.encode())
sock.sendto(packet, (HOST, PORT))

ack_packet, addr = sock.recvfrom(1024)
ack_seq, ack_type, _ = decode(ack_packet)
print(f"received ACK: seq={ack_seq} type={ack_type} from {addr}")
