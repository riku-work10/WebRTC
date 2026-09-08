#!/usr/bin/env bash
# 実践: PIDファイルでHTTPサーバーの起動/停止/状態確認を管理する
# 01(シェルの探索順序)〜10(プロセス・シグナル)で学んだことをまとめて使う小さな実践スクリプト
#
# 使い方:
#   ./serve_ctl.sh start [PORT] [DIR]   # DIR(既定: カレント)を PORT(既定: 8099) で配信開始
#   ./serve_ctl.sh stop
#   ./serve_ctl.sh status

set -u

PID_FILE=".serve_ctl.pid"
LOG_FILE=".serve_ctl.log"

usage() {
  echo "usage: $0 {start|stop|status} [PORT] [DIR]" >&2
  exit 1
}

is_running() {
  # PIDファイルがあり、かつそのPIDが実際に生きていれば0(真)を返す
  [ -f "$PID_FILE" ] || return 1
  local pid
  pid=$(cat "$PID_FILE")
  kill -0 "$pid" 2>/dev/null
}

cmd_start() {
  local port="${1:-8099}"
  local dir="${2:-.}"

  if is_running; then
    echo "already running (pid=$(cat "$PID_FILE"))"
    exit 1
  fi

  if lsof -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "port $port is already in use by another process" >&2
    exit 1
  fi

  # exec で最後にpython3自身に置き換える(execしないとサブシェルの後ろにpython3が
  # 子プロセスとしてぶら下がり、$!で掴んだPIDをkillしてもpython3だけ孤児プロセスとして
  # 残ってしまうことを実験で確認した。詳細はNOTES.mdを参照)
  ( cd "$dir" && exec python3 -m http.server "$port" ) > "$LOG_FILE" 2>&1 &
  local pid=$!
  echo "$pid" > "$PID_FILE"
  sleep 1

  if kill -0 "$pid" 2>/dev/null; then
    echo "started: pid=$pid port=$port dir=$dir (log: $LOG_FILE)"
  else
    echo "failed to start, see $LOG_FILE" >&2
    rm -f "$PID_FILE"
    exit 1
  fi
}

cmd_stop() {
  if ! is_running; then
    echo "not running"
    rm -f "$PID_FILE"
    exit 1
  fi

  local pid
  pid=$(cat "$PID_FILE")
  kill -TERM "$pid"

  for _ in 1 2 3 4 5; do
    kill -0 "$pid" 2>/dev/null || break
    sleep 1
  done

  if kill -0 "$pid" 2>/dev/null; then
    echo "did not stop gracefully, sending SIGKILL"
    kill -9 "$pid"
  fi

  rm -f "$PID_FILE"
  echo "stopped (pid=$pid)"
}

cmd_status() {
  if is_running; then
    echo "running (pid=$(cat "$PID_FILE"))"
  else
    echo "not running"
  fi
}

case "${1:-}" in
  start)  shift; cmd_start "$@" ;;
  stop)   cmd_stop ;;
  status) cmd_status ;;
  *)      usage ;;
esac
