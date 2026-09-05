# 既存のpythonのhttp.serverを拡張して、キャッシュを無効化するためのヘッダーを追加したHTTPサーバー
import http.server


class NoCacheHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()


if __name__ == "__main__":
    http.server.test(HandlerClass=NoCacheHTTPRequestHandler, port=8080)
