#!/bin/bash

while true
do
  python harness.py -g500 > out.txt || exit 1
  echo
  tail stats.txt
  sleep 1
done
