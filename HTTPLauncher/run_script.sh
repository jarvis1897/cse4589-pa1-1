#!/bin/bash

cd ..
cd Grader/remote

git pull
sleep 3
git pull
sleep 3
cd ../..
cd HTTPLauncher

screen -d -m ./start_pa1_http_server.sh 4591
sleep 3

screen -ls

