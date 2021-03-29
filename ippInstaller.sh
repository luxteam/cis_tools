#!/bin/bash

echo $OSTYPE

cd $1

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    ./bootstrapper --action $2 --silent --log-dir logs --eula accept
    
elif [[ "$OSTYPE" == "darwin"* ]]; then
    hdiutil attach $1 -mountpoint /Volumes/IPP
    cd /Volumes/IPP/bootstrapper.app/Contents/MacOS
	./bootstrapper --action $2 --silent --log-dir logs --eula accept
	cd /home
    hdiutil detach /Volumes/IPP
fi





