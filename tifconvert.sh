#!/bin/bash

RESEARCHNAS=~/covert-lab
SCOPEDIR=$RESEARCHNAS/instruments/covert-lab-scope1
ROBOCOPY=$SCOPEDIR/logs/robocopy.log
# cat $RESEARCHNAS/instruments/covert-lab-scope1/logs/robocopy.log | sed 's/\r//' | sed 's/.*m://' | sed -n '/tif/p' | sed 's/\\/\//g' | sed -e 's/^/\/mnt\/covert-lab\/instruments\/covert-lab-scope1/' | sed -e 's/0%.*//' > tifffiles0.txt
cat $ROBOCOPY | sed 's/\r//' | sed 's/.*m://' | sed -n '/tif/p' | sed 's/\\/\//g' | cut -f5 | cut -d" " -f1 | sed -e 's@[a-Z]*:@'"$SCOPEDIR"'@g' > tifffiles.txt
mv $RESEARCHNAS/instruments/covert-lab-scope1/logs/robocopy.log $RESEARCHNAS/instruments/covert-lab-scope1/logs/robocopy_old.log

fix () {
  local TIF=$1
  DIR="$(dirname "$TIF")"
  IN=$TIF
  # FOL=${DIR:28}
  # FILE="$(basename "$TIF")"
  # PNG="${RESEARCHNAS}/instruments/${FOL}/${FILE}"
  # IN=${RESEARCHNAS}/instruments/${FOL}/${FILE}

  echo $IN
  python tiffix.py $IN
  # OUT="${PNG::-4}.png"
  # convert $IN $OUT
}

while read TIF; do
  fix $TIF & 
done < tifffiles.txt
