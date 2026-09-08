# 08 学習記録: ループ

[loop_demo.sh](loop_demo.sh)を実行して確認した。

## `for` の3つの書き方

```bash
for fruit in apple banana cherry; do ... done   # リストを1つずつ
for ((i = 0; i < 3; i++)); do ... done          # C言語風のカウンタ
for f in *.log; do ... done                     # グロブ展開の結果を1つずつ(04で見たグロブがここでも使われる)
```

`for f in *.log`は、シェルが先に`*.log`を`a.log b.log`のように展開してから、`for ... in`のリストとして渡している(グロブの仕組みは`echo`の時と同じ)。マッチするファイルが1つも無い場合は`*.log`という文字列そのものがループ変数に入ってしまう点に注意が必要(`nullglob`オプションで回避可能、未検証)。

## `while` と `until`

```
while [ 条件 ]; do ... done    # 条件が真である間くり返す
until  [ 条件 ]; do ... done   # 条件が偽である間くり返す(条件が真になったら止まる)
```

実行結果は`while count<3`と`until count>=3`で同じ(0,1,2)になった。同じことを書ける2通りの言い回しがあるだけで、可読性のために使い分ける(「〜になるまで待つ」という意味なら`until`の方が自然、など)。

`count=$((count + 1))`は算術展開(`$(( ))`)。文字列の`count`変数を数値として計算し、結果を再び文字列としてcountに代入している。

## `break` / `continue`

```bash
for n in 1 2 3 4 5; do
  [ "$n" -eq 2 ] && continue   # 2はスキップ
  [ "$n" -eq 4 ] && break      # 4で完全に抜ける
  echo "n=$n"
done
# → n=1, n=3 のみ出力(2はcontinueでスキップ、4でbreakして5は実行されない)
```

`continue`はそのループの残り処理を飛ばして次の周回へ、`break`はループ自体を終了する。`if`の代わりに`[ 条件 ] && continue`のように`&&`で短絡評価する書き方も一般的(07で見た「[ ]はコマンドで、終了ステータスを返す」という理解と繋がる)。

## 未消化・今後の課題

- `nullglob`オプション(マッチしないグロブを空にする)
- `while read line; do ... done < file`によるファイルの行読み込み(11の実践スクリプトで使う予定)
