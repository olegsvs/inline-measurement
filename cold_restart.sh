#!/usr/bin/sh
pkill -f bot.py
pkill -f stream_checker.py
pkill -f birthday_checker.py
pkill chromiu
sleep 5
d=$(date +%Y-%m-%d-%H-%M-%S)
cd /home/bot/yepcock-size-bot
mkdir users
mkdir logs
mkdir roulette
mkdir voice_cache
mkdir image_cache
rm wordle.png
rm wordle_screenshot_imgur_link.txt
rm wordle_not_solved_screenshot_imgur_link.txt
mkdir -p ../bot_backup/users_backups_$d/
mkdir -p ../bot_backup/logs_$d/
mv users/* ../bot_backup/users_backups_$d/
mv logs/* ../bot_backup/logs_$d/
sleep 5
nohup python bot.py > logs/nohup_cold.log &
nohup python wordle.py > logs/nohup_wordle_cold.log &
nohup python stream_checker.py > logs/nohup_stream_checker.log &
nohup python birthday_checker.py > logs/nohup_birthday_checker.log &
