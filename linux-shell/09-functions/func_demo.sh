#!/usr/bin/env bash

greet() {
  echo "hello, $1"
}
greet "riku"

add() {
  local a=$1
  local b=$2
  local result=$((a + b))
  echo "$result"
}
sum=$(add 2 3)
echo "sum=$sum"

echo "--- local を付けない場合、グローバルを汚染する ---"
x=100
no_local() {
  x=999
}
no_local
echo "after no_local, x=$x"

y=100
with_local() {
  local y=999
  echo "  inside with_local, y=$y"
}
with_local
echo "after with_local, y=$y"

echo "--- 戻り値は exit status(0-255)。文字列や数値の返却は echo + \$() で行う ---"
is_even() {
  if [ $(($1 % 2)) -eq 0 ]; then
    return 0
  else
    return 1
  fi
}
if is_even 4; then
  echo "4 is even (exit=$?)"
fi
if ! is_even 5; then
  echo "5 is odd"
fi
