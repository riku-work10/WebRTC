#!/usr/bin/env bash
# 意図的に存在しないファイル(nope.txt)を触るため set -e は使わない

printf 'apple\nbanana\ncherry\n' > fruits.txt

echo "--- pipe: catの出力をgrepに渡す ---"
cat fruits.txt | grep an

echo "--- 上書き(>) と 追記(>>) ---"
echo "line1" > out.txt
echo "line2" >> out.txt
echo "line3" > out.txt   # ここで上書きされ、line1/line2は消える
cat out.txt

echo "--- 標準出力(1)と標準エラー出力(2)を別ファイルに分ける ---"
ls fruits.txt nope.txt 2> err.txt 1> ok.txt
echo "ok.txt:"; cat ok.txt
echo "err.txt:"; cat err.txt

echo "--- 2>&1 で標準エラーを標準出力にまとめる ---"
ls fruits.txt nope.txt > combined.txt 2>&1
cat combined.txt

echo "--- ヒアドキュメント(<<) ---"
cat <<EOF
hello $(whoami)
EOF

rm -f fruits.txt out.txt err.txt ok.txt combined.txt
