#!/bin/bash

RESEARCHNAS=~/covert-lab

SCOPEDIR=$RESEARCHNAS/instruments/covert-lab-scope1
ROBOCOPY=$SCOPEDIR/logs/robocopy.log
cat $ROBOCOPY | sed 's/\r//' | sed 's/.*m://' | sed -n '/tif/p' | sed 's/\\/\//g' | cut -f5 | cut -d" " -f1 | sed -e 's@[a-Z]*:@'"$SCOPEDIR"'@g' > tifffiles.txt
mv $RESEARCHNAS/instruments/covert-lab-scope1/logs/robocopy.log $RESEARCHNAS/instruments/covert-lab-scope1/logs/robocopy_old.log

fix () {
  local TIF=$1
  DIR="$(dirname "$TIF")"
  IN=$TIF
  python tiffix.py $IN
}

while read TIF; do
  fix $TIF & 
done < tifffiles.txt
