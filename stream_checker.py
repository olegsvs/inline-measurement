import asyncio
import logging
import os
import calendar
import time
from datetime import datetime
import requests
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from tinydb import TinyDB

# Enable logging
logging.basicConfig(
    filename=datetime.now().strftime('logs/log_stream_checker_%d_%m_%Y_%H_%M.log'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
load_dotenv()

# TG_BOT_TOKEN
TOKEN = os.getenv("TG_BOT_TOKEN")
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_BEARER_TOKEN = os.getenv("TWITCH_BEARER_TOKEN")
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dbStreamChecker = TinyDB('roulette/dbStreamChecker.json')


async def check_stream():
    last_stream_id = -1
    while True:
        try:
            logger.info("Stream checker: running")
            url = 'https://api.twitch.tv/helix/streams?user_login=c_a_k_e'
            my_headers = {
                'Client-ID': TWITCH_CLIENT_ID,
                'Authorization': TWITCH_BEARER_TOKEN
            }
            response = requests.get(url, headers=my_headers, timeout=15)
            data = response.json()['data']
            if len(data) != 0 and data[0]['type'] == 'live':
                stream = data[0]
                logger.info("Stream checker: streaming")
                stream_id = stream['id']
                if last_stream_id != stream_id:
                    last_stream_id = stream_id
                    msg = "👾 C_a_k_e завёл стрим! Категория: " + stream['game_name'] + "\nНазвание стрима - " + stream[
                        'title'] + "\nhttps://www.twitch.tv/c_a_k_e/?t=" + str(calendar.timegm(time.gmtime()))
                    msg2 = "👾 C_a_k_e завёл стрим! Категория: " + stream['game_name'] + "\nНазвание стрима - " + stream[
                        'title'] + "\nhttps://www.twitch.tv/c_a_k_e"
                    thumbnail = stream['thumbnail_url']
                    alert_for_stream_id_showed = dbStreamChecker.all()
                    send_msg = True
                    if not alert_for_stream_id_showed:
                        dbStreamChecker.insert({"last_stream_id": last_stream_id})
                    else:
                        for showed_stream_id in alert_for_stream_id_showed:
                            if str(last_stream_id) in str(showed_stream_id):
                                send_msg = False
                    if send_msg:
                        logger.info("Stream checker: Send msg")
                        dbStreamChecker.insert({"last_stream_id": last_stream_id})
                        if thumbnail is not None:
                            thumbnail += '?t=' + str(calendar.timegm(time.gmtime()))
                            await bot.send_photo(chat_id=-1001567412048, photo=thumbnail.replace('{width}','1920').replace('{height}','1080'), caption=msg2)
                        else:
                            await bot.send_message(chat_id=-1001567412048, text=msg)
                    else:
                        logger.info("Stream checker: Msg already sended")
                    await asyncio.sleep(60 * 10)
                else:
                    await asyncio.sleep(60 * 10)
            else:
                logger.info("Stream checker: Not streaming")
                await asyncio.sleep(30)
        except Exception as e:
            logger.error('Stream check failed: ' + str(e))
            await asyncio.sleep(30)


def main():
    asyncio.run(check_stream())


if __name__ == '__main__':
    main()
