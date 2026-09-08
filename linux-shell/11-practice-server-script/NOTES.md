# 11 学習記録: 実践 — サーバー起動/停止スクリプト

[serve_ctl.sh](serve_ctl.sh)は、01〜10で学んだこと(コマンド探索、変数、クォート、引数と終了ステータス、`if`/`case`、`local`関数、`kill`/`trap`)を一つにまとめた実践スクリプト。WebRTC側の各phaseにある`serve.py`(簡易HTTPサーバー)を素材に、「起動・停止・状態確認」をPIDファイルで管理する。

```
./serve_ctl.sh start [PORT] [DIR]   # 例: ./serve_ctl.sh start 8099 ../../phase-01-camera-viewer
./serve_ctl.sh stop
./serve_ctl.sh status
```

## 実際に見つけたバグ: サブシェル + バックグラウンドで孤児プロセスが残る

最初、サーバー起動部分をこう書いていた:

```bash
( cd "$dir" && python3 -m http.server "$port" ) > "$LOG_FILE" 2>&1 &
local pid=$!
```

実際に`start`→`lsof -iTCP:8099 -sTCP:LISTEN`で確認したところ、`$!`で取れたPID(65219)と、実際にポートをlistenしているPythonプロセスのPID(65220)が**一致しない**ことに気づいた。

```
$! で取ったPID: 65219   ← ( ) サブシェル(bash)自身のPID
listenしてるPID: 65220   ← サブシェルが fork して起動した python3 の子プロセス
```

`( cmd1 && cmd2 )`は「サブシェル(新しいbashプロセス)を1つ立てて、その中でcmd1とcmd2を順に実行する」という意味。`cmd2`(python3)は、サブシェルが**さらにforkして起動する子プロセス**になる(bashが自動で「最後のコマンドだから自分をpython3に置き換える」という最適化をしなかった)。

このため`serve_ctl.sh stop`で`$!`(=65219, サブシェル)に`kill -TERM`しても、サブシェル自身は終了するが、**その子であるpython3(65220)には何もシグナルが届かず、孤児プロセス(PPID=1)としてポートを掴んだまま残り続けた**(`ps -p 65220`で`PPID 1`になっていることを確認)。ポートが解放されないため、次に`start`しようとすると`lsof`のチェックに引っかかって失敗する状態になっていた。

## 修正: `exec` でサブシェル自身をpython3に置き換える

```bash
( cd "$dir" && exec python3 -m http.server "$port" ) > "$LOG_FILE" 2>&1 &
```

`exec`を付けると、「新しいプロセスをforkする」のではなく「今のプロセス(サブシェル)の中身をpython3に置き換える」動作になる。修正後に同じ実験をしたところ:

```
$! で取ったPID:   65282
listenしてるPID:  65282   ← 一致した
```

`stop`後に`lsof -iTCP:8099 -sTCP:LISTEN`を実行しても何も表示されなくなり、孤児プロセスが残らないことを確認した。

## この実践で使った要素の対応表

```
type / $PATH                     → 01: python3, lsof, curlの実体がPATH上のどこにあるか
2>&1, > "$LOG_FILE"               → 02: サーバーの標準出力/エラーをログファイルにまとめる
"${1:-8099}"                      → 03/06: 引数が無い時のデフォルト値、変数のクォート習慣
[ -f "$PID_FILE" ], [[ ]] を使わずPOSIX [ ] で統一  → 07
case "${1:-}" in start) ... ;; esac  → 08で扱わなかった新しい分岐構文(パターンマッチ)
local pid, local port             → 09: 関数内のグローバル汚染を避ける
$!, kill -TERM, kill -0, trap的な考え方 → 10: プロセス管理・シグナル
```

`kill -0 PID`は「シグナルを送らずに、そのPIDが存在するかどうかだけ確認する」特殊な使い方(`is_running`関数で使用)。存在すれば終了ステータス0、無ければ非0を返すので、07で学んだ「`if`はコマンドの終了ステータスを見ているだけ」という理解がそのまま活きた。

## 未消化・今後の課題

- `case`のパターンマッチ構文自体の詳細(`*)`のデフォルト分岐など)
- このスクリプトをWebRTC側の`phase-01`/`phase-02`の`serve.py`(固定ポート8080/8081)に対しても使えるように拡張する(現状は`python3 -m http.server`固定でCache-Control無効化には対応していない)
