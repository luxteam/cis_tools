#!/bin/bash

if [[ "$2" == "install" ]]; then
    apt-get install libomp-dev
else
    apt-get remove libomp-dev
fi

cd $1
./bootstrapper --action $2 --silent --log-dir logs --eula accept
