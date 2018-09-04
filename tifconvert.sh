#!/bin/bash

RESEARCHNAS=/mnt/covert-lab
SCOPEDIR=$RESEARCHNAS/instruments/covert-lab-scope1
ROBOCOPY=$SCOPEDIR/logs/robocopy.log

if [ ! -f tifffiles.txt ]; then
  grep -I .tif $ROBOCOPY|grep -v ERROR | sed 's/\\/\//g'|cut -f5|sed 's/.tif.*/.tif/' | sed -e 's@[a-Z]*:@'"$SCOPEDIR"'@g' > tifffiles.txt
  sudo mv $RESEARCHNAS/instruments/covert-lab-scope1/logs/robocopy.log $RESEARCHNAS/instruments/covert-lab-scope1/logs/robocopy_old.log
  
  sudo ~/.pyenv/shims/python tiffix.py tifffiles.txt 

  mv tifffiles.txt tifffiles_old.txt
fi

#while read line; do
#rm $line
#done < corrupted.txt

