# 05 学習記録: シェルスクリプトの基本

[hello.sh](hello.sh)を使って確認した。

## 実行権限がないと実行できない

```
-rw-r--r--@ ... hello.sh
./hello.sh
   → permission denied: ./hello.sh   (exit=126)
```

`./hello.sh`(ファイルを直接実行)は、OSが「これは実行可能なファイルか」をパーミッションビット(`x`)で確認する。`rw-`にはxが無いため拒否された。

一方、`bash hello.sh`のように「bashにファイルを読ませて実行する」方式は、`hello.sh`自体は単なるテキストファイルとして読まれるだけなので、実行権限は不要だった。

```
chmod +x hello.sh
-rwxr-xr-x@ ... hello.sh
./hello.sh   → hello, shell script    (成功)
```

## shebang(`#!`)の役割

```
#!/usr/bin/env bash
```

`./hello.sh`のように直接実行した場合、OSはファイルの先頭2バイトが`#!`かどうかを見て、それ以降に書かれたインタプリタ(この場合`/usr/bin/env bash`)にファイルパスを渡して代わりに実行させる。`bash hello.sh`のように明示的にインタプリタを指定して実行した場合は、shebang行はただのコメントとして無視される(bash自身が読んでも実害はない)。

`#!/usr/bin/env bash`は`#!/bin/bash`と違い、`$PATH`上から`bash`を探して使う書き方。環境によって`bash`の場所が違う(後述)場合に、より移植性が高い。

## macOSのbashは古い(発見)

```
$ env bash --version
GNU bash, version 3.2.57(1)-release (arm64-apple-darwin25)
```

macOSに標準で入っている`/bin/bash`はバージョン3.2で止まっている(Apple社がGPLv3ライセンスを避けているため)。連想配列(`declare -A`)などbash4以降の機能はこのままでは使えない。今後の課題として、Homebrewで新しいbashを入れるか、その機能が必要な場面ではzshで書くかを検討する。

## 未消化・今後の課題

- Homebrewの新しいbash(`brew install bash`)の有無を確認し、必要なら導入する
- `set -euo pipefail`(安全なスクリプトの定石)の意味を11(実践)で使いながら理解する
