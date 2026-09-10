from dataclasses import dataclass

from stun_query import get_host_ip, get_srflx_candidate

# ICE(Interactive Connectivity Establishment, RFC 8445)の簡易実装。
# 本物のICEは相手とSTUNメッセージを送り合って実際に疎通確認するが、
# ここでは「1. candidateを集める」「2. 優先度を計算する」「3. ペアを並べ替えて選ぶ」
# という考え方の流れだけを追う(実際の疎通チェックはしない)

COMPONENT_RTP = 1

# RFC 8445 5.1.2.2: candidate種別ごとの優先度の目安(高いほど優先)
TYPE_PREFERENCE = {"host": 126, "srflx": 100, "relay": 0}


@dataclass
class Candidate:
    foundation: str
    component: int
    transport: str
    ip: str
    port: int
    typ: str  # host / srflx / relay
    local_pref: int = 65535

    @property
    def priority(self) -> int:
        # RFC 8445 5.1.2.1: candidate自体の優先度
        type_pref = TYPE_PREFERENCE[self.typ]
        return (2 ** 24) * type_pref + (2 ** 8) * self.local_pref + (2 ** 0) * (256 - self.component)

    def to_sdp_line(self) -> str:
        # SDPのa=candidate行と同じ書式(Phase 10で実際のSDPを読むときの伏線)
        return (f"candidate:{self.foundation} {self.component} {self.transport} "
                f"{self.priority} {self.ip} {self.port} typ {self.typ}")


def gather_local_candidates() -> list[Candidate]:
    candidates = []

    host_ip = get_host_ip()
    candidates.append(Candidate(foundation="1", component=COMPONENT_RTP, transport="udp",
                                 ip=host_ip, port=54321, typ="host"))
    print(f"[gather] host candidate: {host_ip}:54321 (自分のPrivate IP、そのまま使えるなら一番速い)")

    try:
        public_ip, public_port, local_port = get_srflx_candidate()
        candidates.append(Candidate(foundation="2", component=COMPONENT_RTP, transport="udp",
                                     ip=public_ip, port=public_port, typ="srflx"))
        print(f"[gather] srflx candidate: {public_ip}:{public_port} "
              f"(STUNで分かったNAT越しのPublic側、ローカルport={local_port})")
    except OSError as e:
        print(f"[gather] srflx candidate取得失敗(STUNサーバーに届かない?): {e}")

    # relay candidate(TURN経由)はTURNサーバーが必要なのでPhase 16で扱う。ここでは省略

    return candidates


def pair_priority(local: Candidate, remote: Candidate, is_controlling: bool) -> int:
    # RFC 8445 6.1.2.3: G=controlling側の優先度, D=controlled側の優先度
    g = local.priority if is_controlling else remote.priority
    d = remote.priority if is_controlling else local.priority
    return (2 ** 32) * min(g, d) + 2 * max(g, d) + (1 if g > d else 0)


def build_remote_peer_candidates() -> list[Candidate]:
    # 本来は相手からSDP/シグナリング経由で届く候補(Phase 11で実際にやる)。
    # ここでは説明のため、別ネットワークにいる相手を想定して手で作る
    return [
        Candidate(foundation="1", component=COMPONENT_RTP, transport="udp",
                  ip="192.168.1.50", port=51000, typ="host"),
        Candidate(foundation="2", component=COMPONENT_RTP, transport="udp",
                  ip="203.0.113.10", port=51001, typ="srflx"),
    ]


if __name__ == "__main__":
    print("=== 1. candidateを集める(自分側) ===")
    local_candidates = gather_local_candidates()
    for c in local_candidates:
        print(f"  {c.to_sdp_line()}")

    print()
    print("=== 2. 相手側candidate(シグナリングで受け取ったと仮定) ===")
    remote_candidates = build_remote_peer_candidates()
    for c in remote_candidates:
        print(f"  {c.to_sdp_line()}")

    print()
    print("=== 3. 全ペアを優先度順に並べる(自分がcontrolling側と仮定) ===")
    pairs = []
    for local in local_candidates:
        for remote in remote_candidates:
            pairs.append((pair_priority(local, remote, is_controlling=True), local, remote))

    pairs.sort(key=lambda p: p[0], reverse=True)
    for priority, local, remote in pairs:
        print(f"  priority={priority}: local({local.typ})={local.ip}:{local.port} "
              f"<-> remote({remote.typ})={remote.ip}:{remote.port}")

    best = pairs[0]
    print()
    print(f"[選択] 実際のICEはこの並び順で先頭から疎通確認(STUN Binding Request)を試み、"
          f"最初に成功したペアを使う。優先度が最も高いのは "
          f"local({best[1].typ}) <-> remote({best[2].typ})")
