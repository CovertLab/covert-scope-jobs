#!/bin/bash



cat $RESEARCHNAS/instruments/covert-lab-scope1/logs/robocopy.log | sed 's/\r//' | sed 's/.*m://' | sed -n '/tif/p' | sed 's/\\/\//g' | sed -e 's/^/\/mnt\/covert-lab\/instruments\/covert-lab-scope1/' | sed -e 's/0%.*//' > tifffiles.txt


fix () {
  local TIF=$1
  DIR="$(dirname "$TIF")"
  FOL=${DIR:28}
  FILE="$(basename "$TIF")"
  PNG="${RESEARCHNAS}/instruments/${FOL}/${FILE}"
  IN=${RESEARCHNAS}/instruments/${FOL}/${FILE}
  OUT="${PNG::-4}.png"

  python tiffix.py $IN
  convert $IN $OUT
}

while read TIF; do
  fix $TIF & 
done < tifffiles.txt
