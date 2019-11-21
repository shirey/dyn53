#!/bin/bash
sleep 1200
WD="$(dirname "$0")"
source $WD/../py3env/bin/activate
cd $WD
python dyn53.py
if [ $? -eq 0 ]
then
  exit 0
else
  exit 1
fi
