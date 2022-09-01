#!/bin/bash

if [ $# -lt 1 ]
then
        echo "Usage : $0 <port number>"
        exit
fi

cd terraform
gunicorn -w 1 --threads 12 -k gevent -b 0.0.0.0:$1 appflask:app