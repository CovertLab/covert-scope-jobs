#!/bin/bash

DELAY=28800 # wait 8 hours between runs

while true
do
  START=$(date +%s)
  bash tifconvert.sh
  END=$(date +%s)
  DELTA=$(($END-$START))
  if [[ $DELTA -lt $DELAY ]]; then
    SLEEP=$(($DELAY-$DELTA))
  else
    SLEEP=0
  fi
  sleep $SLEEP
done
