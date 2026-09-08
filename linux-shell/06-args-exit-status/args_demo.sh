#!/usr/bin/env bash
echo "script name (\$0): $0"
echo "arg count (\$#):   $#"
echo "all args (\$@):    $@"
echo "1st arg (\$1):     $1"
echo "2nd arg (\$2):     $2"

for arg in "$@"; do
  echo "  loop: [$arg]"
done

if [ "$1" = "fail" ]; then
  echo "exiting with 1 on purpose"
  exit 1
fi

exit 0
