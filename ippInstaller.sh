#!/bin/bash

cd $1
./bootstrapper --action $2 --silent --log-dir logs --eula accept
