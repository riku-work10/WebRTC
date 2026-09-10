import socket
import sys

from stun_format import build_binding_request, parse_binding_response

# 公開STUNサーバー。STUNサーバー自体は「リクエストがどこから来たか(Public IP:Port)」を
# そのまま送り返すだけの単純なサーバー
STUN_SERVER = sys.argv[1] if len(sys.argv) > 1 else "stun.l.google.com"
STUN_PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 19302

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(3)

request, transaction_id = build_binding_request()
sock.sendto(request, (STUN_SERVER, STUN_PORT))
print(f"[client] {STUN_SERVER}:{STUN_PORT} へBinding Requestを送信")

try:
    response, addr = sock.recvfrom(2048)
    print(f"[client] {addr} から応答を受信 ({len(response)}byte)")

    public_ip, public_port = parse_binding_response(response, transaction_id)
    local_ip, local_port = sock.getsockname()

    print()
    print(f"[結果] このソケットのPrivate側: {local_ip}:{local_port}")
    print(f"[結果] NAT越しに見えるPublic側 : {public_ip}:{public_port}")
    print()
    print("Private側とPublic側のPortが違う場合、NATがPortも書き換えている(Symmetric NAT等)。")
    print("同じPCから複数回実行してPublic Portが毎回変わるなら、宛先ごとにマッピングを")
    print("変える種類のNAT(Symmetric NAT)であり、STUNだけでは越えられない可能性が高い。")
except socket.timeout:
    print("[client] タイムアウト: STUNサーバーから応答がない(UDPがブロックされている?)")
finally:
    sock.close()
