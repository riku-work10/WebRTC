# Linux / Shell 学習

WebRTCの学習フェーズ(`phase-01`〜)とは別トラックで、Linuxコマンド・シェル・シェルスクリプトそのものを学ぶためのディレクトリ。

シェルの操作で必要になったコマンドは引き続き[../LINUX_COMMANDS.md](../LINUX_COMMANDS.md)に集約し、ここでは「シェル自体の仕組み・文法」を最小コードで確認しながら学ぶ。

サイクル: 最小コードを書く → 実行する → 挙動を観察する → 変更する → 再実行する → 理解する(WebRTC側のフェーズと同じ進め方)

補足: 開発機はmacOS(デフォルトシェルは`zsh`)。教材や慣習の多くは`bash`前提のことが多いため、両者の違いに触れる場面ではその都度記録する([05](05-script-basics/NOTES.md)でmacOS標準の`/bin/bash`が3.2と古いことが判明)。

## 進捗

- [x] 01: シェルとは何か — [01-shell-basics/NOTES.md](01-shell-basics/NOTES.md)
- [x] 02: 基本コマンドとパイプ・リダイレクト — [02-pipes-redirects/NOTES.md](02-pipes-redirects/NOTES.md)
- [x] 03: シェル変数と環境変数 — [03-variables/NOTES.md](03-variables/NOTES.md)
- [x] 04: 引用符とグロブ — [04-quoting-globbing/NOTES.md](04-quoting-globbing/NOTES.md)
- [x] 05: シェルスクリプトの基本 — [05-script-basics/NOTES.md](05-script-basics/NOTES.md)
- [x] 06: 引数と終了ステータス — [06-args-exit-status/NOTES.md](06-args-exit-status/NOTES.md)
- [x] 07: 条件分岐 — [07-conditionals/NOTES.md](07-conditionals/NOTES.md)
- [x] 08: ループ — [08-loops/NOTES.md](08-loops/NOTES.md)
- [x] 09: 関数とローカル変数 — [09-functions/NOTES.md](09-functions/NOTES.md)
- [x] 10: プロセスとジョブ制御 — [10-process-job-control/NOTES.md](10-process-job-control/NOTES.md)
- [x] 11: 実践: 自作サーバー起動/停止スクリプト — [11-practice-server-script/NOTES.md](11-practice-server-script/NOTES.md)(サブシェル+バックグラウンドで孤児プロセスが残るバグを実際に踏んで`exec`で修正した)

## 各回で未消化として残っている主なトピック

- `.zprofile`/`.zshrc`の中身を読んでPATH重複の原因を特定する([03](03-variables/NOTES.md))
- `{}`によるブレース展開、`$'...'`によるエスケープ展開([04](04-quoting-globbing/NOTES.md))
- `case`文のパターンマッチ構文自体の詳細、`[[ ]]`の`=~`正規表現マッチ([07](07-conditionals/NOTES.md))
- `nullglob`オプション、`while read line; do ... done < file`によるファイル行読み込み([08](08-loops/NOTES.md))
- `fg`/`bg`/ジョブ番号でのジョブ制御、SIGINT/SIGKILLとの違い([10](10-process-job-control/NOTES.md))

これらは次のサイクルで扱う。追加のトピックが必要になったら`README.md`の進捗リストに追記する。

## メモの残し方

各項目を学んだら、このディレクトリ配下に`XX-トピック名/`を作り、試したスクリプトと気づきを`NOTES.md`に残す(WebRTC側の`phase-XX/NOTES.md`と同じ形式)。
