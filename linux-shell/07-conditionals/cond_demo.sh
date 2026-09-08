#!/usr/bin/env bash

NUM=5
if [ "$NUM" -gt 3 ]; then
  echo "[ ] : $NUM is greater than 3"
fi

if [[ $NUM -gt 3 && $NUM -lt 10 ]]; then
  echo "[[ ]] : $NUM is between 3 and 10"
fi

FILE="cond_demo.sh"
if [ -f "$FILE" ]; then
  echo "-f : $FILE exists as a regular file"
fi
if [ -x "$FILE" ]; then
  echo "-x : $FILE is executable"
else
  echo "-x : $FILE is NOT executable"
fi

STR=""
if [ -z "$STR" ]; then
  echo "-z : STR is empty"
fi

echo "--- test コマンドそのもの ---"
test 1 -eq 1; echo "test 1 -eq 1 -> exit=$?"
test 1 -eq 2; echo "test 1 -eq 2 -> exit=$?"

echo "--- [[ ]] のパターンマッチ(bashの拡張機能) ---"
NAME="hello.txt"
if [[ $NAME == *.txt ]]; then
  echo "[[ ]] : $NAME matches *.txt"
fi
