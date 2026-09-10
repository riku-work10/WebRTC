import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

HOST = "127.0.0.1"
PORT = 9004

# WebRTC自体にはSDP/candidateを相手に届ける仕組みが無い(仕様上「シグナリング方法は決めない」)。
# ここではroomごとにoffer/answer/candidateをメモリに置いておくだけの、最小のHTTP polling方式サーバーを自作する。
#
# 流れ:
#   offerer: POST /rooms/<room>/offer            → offerを置く
#   answerer: GET  /rooms/<room>/offer?wait=10    → offerが来るまで(最大10秒)待って取得
#   answerer: POST /rooms/<room>/answer
#   offerer: GET  /rooms/<room>/answer?wait=10
#   両者   : POST/GET /rooms/<room>/candidates    → ICE candidateを送り合う(こちらはlist)
lock = threading.Lock()
rooms: dict[str, dict] = {}


def get_room(name: str) -> dict:
    if name not in rooms:
        rooms[name] = {"offer": None, "answer": None, "candidates": []}
    return rooms[name]


class SignalingHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[server] {self.address_string()} {fmt % args}")

    def _send_json(self, status: int, body: dict) -> None:
        payload = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length))

    def do_POST(self):
        parsed = urlparse(self.path)
        parts = parsed.path.strip("/").split("/")  # ["rooms", "<room>", "offer"]
        if len(parts) != 3 or parts[0] != "rooms":
            return self._send_json(404, {"error": "not found"})

        room_name, kind = parts[1], parts[2]
        body = self._read_json()

        with lock:
            room = get_room(room_name)
            if kind in ("offer", "answer"):
                room[kind] = body
                print(f"[server] room={room_name} に {kind} を保存")
            elif kind == "candidates":
                room["candidates"].append(body)
                print(f"[server] room={room_name} にcandidateを追加(計{len(room['candidates'])}件)")
            else:
                return self._send_json(404, {"error": "unknown kind"})

        self._send_json(200, {"ok": True})

    def do_GET(self):
        parsed = urlparse(self.path)
        parts = parsed.path.strip("/").split("/")
        if len(parts) != 3 or parts[0] != "rooms":
            return self._send_json(404, {"error": "not found"})

        room_name, kind = parts[1], parts[2]
        query = parse_qs(parsed.query)
        wait_seconds = float(query.get("wait", ["0"])[0])

        if kind in ("offer", "answer"):
            # long polling: 値が置かれるまで、タイムアウトまでポーリングし続ける
            deadline = time.time() + wait_seconds
            while True:
                with lock:
                    value = get_room(room_name).get(kind)
                if value is not None or time.time() >= deadline:
                    return self._send_json(200, {kind: value})
                time.sleep(0.2)

        elif kind == "candidates":
            since = int(query.get("since", ["0"])[0])
            with lock:
                candidates = get_room(room_name)["candidates"][since:]
            return self._send_json(200, {"candidates": candidates, "next_since": since + len(candidates)})

        return self._send_json(404, {"error": "unknown kind"})


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), SignalingHandler)
    print(f"Signaling server (HTTP polling) listening on {HOST}:{PORT}")
    server.serve_forever()
