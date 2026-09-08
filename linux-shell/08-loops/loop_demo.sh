#!/usr/bin/env bash

echo "--- for: リストを回す ---"
for fruit in apple banana cherry; do
  echo "  fruit=$fruit"
done

echo "--- for: C言語風(範囲) ---"
for ((i = 0; i < 3; i++)); do
  echo "  i=$i"
done

echo "--- for: ファイル一覧(グロブ)を回す ---"
touch a.log b.log
for f in *.log; do
  echo "  file=$f"
done
rm -f a.log b.log

echo "--- while: 条件が真の間 ---"
count=0
while [ "$count" -lt 3 ]; do
  echo "  count=$count"
  count=$((count + 1))
done

echo "--- until: 条件が真になるまで(whileの逆) ---"
count=0
until [ "$count" -ge 3 ]; do
  echo "  count=$count"
  count=$((count + 1))
done

echo "--- break / continue ---"
for n in 1 2 3 4 5; do
  if [ "$n" -eq 2 ]; then
    continue
  fi
  if [ "$n" -eq 4 ]; then
    break
  fi
  echo "  n=$n"
done
