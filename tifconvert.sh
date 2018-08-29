#!/bin/bash

RESEARCHNAS=/mnt/covert-lab
SCOPEDIR=$RESEARCHNAS/instruments/covert-lab-scope1
ROBOCOPY=$SCOPEDIR/logs/robocopy.log

if [ ! -f tifffiles.txt ]; then
  cat $ROBOCOPY | sed 's/\r//' | sed 's/.*m://' | sed -n '/tif/p' | sed 's/\\/\//g' | cut -f5 | cut -d" " -f1 | sed -e 's@[a-Z]*:@'"$SCOPEDIR"'@g' > tifffiles.txt
  sudo mv $RESEARCHNAS/instruments/covert-lab-scope1/logs/robocopy.log $RESEARCHNAS/instruments/covert-lab-scope1/logs/robocopy_old.log
  
  sudo ~/.pyenv/shims/python tiffix.py tifffiles.txt 

  mv tifffiles.txt tifffiles_old.txt
fi

