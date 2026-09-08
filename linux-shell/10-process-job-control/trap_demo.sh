#!/usr/bin/env bash
trap 'echo "SIGTERM(15) received, cleaning up..."; exit 0' TERM
echo "pid=$$ sleeping, send: kill -TERM $$"
sleep 30
echo "this line should not print if killed"
