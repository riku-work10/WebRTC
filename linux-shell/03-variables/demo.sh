#!/usr/bin/env bash

FOO=bar
echo "1) 通常の変数は今のシェルの中でしか見えない: $FOO"

echo "2) 子プロセス(bash -c)からは見えないはず:"
bash -c 'echo "   subshell: FOO=[$FOO]"'

export FOO
echo "3) export した後は、子プロセスにも環境変数として引き継がれる:"
bash -c 'echo "   subshell: FOO=[$FOO]"'

echo "4) env(環境変数だけ) と set(シェル変数+関数も含む全部) の違い:"
echo "   env の行数:   $(env | wc -l | tr -d ' ')"
echo "   set の行数:   $(set | wc -l | tr -d ' ')"
