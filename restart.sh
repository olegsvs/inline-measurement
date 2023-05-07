#!/usr/bin/sh
pkill -f bot.py
pkill -f stream_checker.py
pkill -f birthday_checker.py
sleep 5
nohup python3.10 bot.py > logs/nohup.log &
#nohup python3.10 stream_checker.py > logs/nohup_stream_checker.log &
nohup python3.10 birthday_checker.py > logs/nohup_birthday_checker.log &
