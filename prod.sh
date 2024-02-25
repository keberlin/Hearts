#!/usr/bin/bash

export LC_ALL=en_US

SCRIPTPATH=`dirname "$0"`

cd $SCRIPTPATH

source venv/bin/activate

#gunicorn --workers 1 --threads 5 --timeout 0 --bind :6050 wsgi:app

while true
do
  python harness.py -g5
  sleep 1
done
