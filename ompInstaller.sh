#!/bin/bash

echo $OSTYPE

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [[ "$1" == "install" ]]; then
    		apt-get $1 libomp-dev
	else
    		apt-get $1 libomp-dev
	fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
        if [[ "$1" == "install" ]]; then
                brew $1 libomp
        else
                brew $1 libomp
        fi
fi
