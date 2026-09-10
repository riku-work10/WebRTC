import json
import socket
import urllib.request

# NAT(Network Address Translation): ルーターがPrivate IP:Portを
# Public IP:Portに書き換えて外部と通信させる仕組み。
# このPC自身は「自分のPrivate IPしか」知らず、外の世界からどう見えているか(Public IP)は
# 外部サーバーに聞かない限り分からない。


def get_private_ip() -> str:
    # UDPソケットのconnect()は実際にパケットを送らない(3-way handshakeが無いため)。
    # OSに「この宛先に出すならどの経路(=どのNIC)を使うか」を決めさせ、
    # そのNICに割り当てられたPrivate IPをgetsockname()で読み取るテクニック。
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]


def get_public_ip() -> str:
    # 外部サービスに「あなたのIPは?」と聞く。
    # サーバー側から見えるsrc IPは、途中のNATやルーターで書き換えられた後のPublic IP。
    with urllib.request.urlopen("https://api.ipify.org?format=json", timeout=5) as res:
        data = json.load(res)
        return data["ip"]


if __name__ == "__main__":
    private_ip = get_private_ip()
    print(f"[private] このPCがLAN内で使っているIP: {private_ip}")

    try:
        public_ip = get_public_ip()
        print(f"[public]  外部から見えるIP(ルーターのWAN側): {public_ip}")
    except OSError as e:
        print(f"[public]  取得失敗(オフライン?): {e}")

    print()
    print("private と public が一致しない場合、その間にNATが挟まっている。")
    print("次のコマンドでも確認できる:")
    print("  ip addr show           (Linux: 各インターフェースのPrivate IP)")
    print("  ifconfig                (macOS: 同上)")
    print("  traceroute api.ipify.org  (自分からのホップ=経由ルーターを表示)")
