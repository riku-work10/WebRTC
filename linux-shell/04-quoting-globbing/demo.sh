#!/usr/bin/env bash

NAME=world
echo "--- クォートの違い ---"
echo 'single quote: $NAME'
echo "double quote: $NAME"
echo no quote: $NAME

echo "--- コマンド置換: バッククォート と \$() ---"
echo `echo nested`
echo $(echo nested)

touch a.txt b.txt c.log

echo "--- glob: * ---"
echo *.txt
echo "--- glob: ? ---"
echo ?.txt
echo "--- glob: [] ---"
echo [ab].txt

echo "--- クォート無し変数展開による単語分割 ---"
MULTI="one two three"
set -- $MULTI
echo "count=$#"
set -- "$MULTI"
echo "count(quoted)=$#"

rm -f a.txt b.txt c.log
