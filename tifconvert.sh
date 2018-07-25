#!/bin/bash

cat robocopy.log | sed 's/.*m://' | sed -n '/tif/p' | sed 's/\\/\//g' | sed -e 's/^/\/mnt\/covert-lab\/instruments\/covert-lab-scope1/' > tifffiles.txt


convert () {
  local TIF=$1
  DIR="$(dirname "$TIF")"
  FILE="$(basename "$TIF" .tif)"
  PNG="${DIR}/$FILE.png"

  python tiffix.py $TIF
  convert $TIF $PNG
}

while read TIF; do
  convert $TIF & 
done < tifffiles.txt
