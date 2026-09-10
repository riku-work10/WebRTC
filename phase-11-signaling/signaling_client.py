import json
import sys
import time
import urllib.request

HOST = "127.0.0.1"
PORT = 9004
ROOM = "test-room"
BASE = f"http://{HOST}:{PORT}/rooms/{ROOM}"


def post(kind: str, body: dict) -> None:
    data = json.dumps(body).encode()
    req = urllib.request.Request(f"{BASE}/{kind}", data=data, method="POST",
                                  headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as res:
        json.load(res)


def get(kind: str, wait: int = 0) -> dict:
    with urllib.request.urlopen(f"{BASE}/{kind}?wait={wait}") as res:
        return json.load(res)


def get_candidates(since: int) -> tuple[list, int]:
    with urllib.request.urlopen(f"{BASE}/candidates?since={since}") as res:
        data = json.load(res)
        return data["candidates"], data["next_since"]


def run_offerer() -> None:
    print("[offerer] SDP offerを作成して送信(本来はpc.createOffer()の結果)")
    post("offer", {"type": "offer", "sdp": "v=0...(dummy offer sdp)"})

    print("[offerer] 自分のICE candidateを送信")
    post("candidates", {"from": "offerer", "candidate": "candidate:1 1 udp 2130706431 127.0.0.1 50000 typ host"})

    print("[offerer] answererからのanswerを待つ(long polling, 最大30秒)")
    result = get("answer", wait=30)
    if result["answer"] is None:
        print("[offerer] タイムアウト: answerが届かなかった")
        return
    print(f"[offerer] answer受信: {result['answer']}")

    since = 0
    print("[offerer] answerer側のcandidateを取得")
    for _ in range(5):
        candidates, since = get_candidates(since)
        for c in candidates:
            print(f"[offerer] candidate受信: {c}")
        if candidates:
            break
        time.sleep(1)


def run_answerer() -> None:
    print("[answerer] offererからのofferを待つ(long polling, 最大30秒)")
    result = get("offer", wait=30)
    if result["offer"] is None:
        print("[answerer] タイムアウト: offerが届かなかった")
        return
    print(f"[answerer] offer受信: {result['offer']}")

    print("[answerer] SDP answerを作成して送信(本来はpc.createAnswer()の結果)")
    post("answer", {"type": "answer", "sdp": "v=0...(dummy answer sdp)"})

    print("[answerer] 自分のICE candidateを送信")
    post("candidates", {"from": "answerer", "candidate": "candidate:1 1 udp 2130706431 127.0.0.1 51000 typ host"})

    since = 0
    print("[answerer] offerer側のcandidateを取得")
    for _ in range(5):
        candidates, since = get_candidates(since)
        for c in candidates:
            print(f"[answerer] candidate受信: {c}")
        if candidates:
            break
        time.sleep(1)


if __name__ == "__main__":
    role = sys.argv[1] if len(sys.argv) > 1 else "offerer"
    if role == "offerer":
        run_offerer()
    elif role == "answerer":
        run_answerer()
    else:
        print("usage: python3 signaling_client.py [offerer|answerer]")
