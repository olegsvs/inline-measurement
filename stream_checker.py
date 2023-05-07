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
import vk_api
from vk_api import VkUpload
import tg_logger
import replicate
import replicate.version
import replicate.exceptions
from typing import Tuple
from typing import Optional

# Enable logging
logging.basicConfig(
    filename=datetime.now().strftime('logs/log_stream_checker_%d_%m_%Y_%H_%M.log'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
load_dotenv()
# TG_BOT_TOKEN
TOKEN = os.getenv("TG_BOT_TOKEN")
TG_LOGGER_TOKEN = os.getenv("TG_LOGGER_TOKEN")
TG_ADMIN_ID = os.getenv("OWNER_USER_ID")
#tg_logger.setup(logger, token=TG_LOGGER_TOKEN, users=[int(TG_ADMIN_ID)])
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_BEARER_TOKEN = os.getenv("TWITCH_BEARER_TOKEN")
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
os.environ["REPLICATE_API_TOKEN"] = '24156ea0e1c034c6af17a826b7d167b2b5debd72'


def get_replicate_response(
    text: str
) -> Tuple[str, Optional[str]]:
    if not text:
        return "", "No text provided"
    try:
        #model = replicate.models.get("prompthero/openjourney")
        #version = model.versions.get("9936c2001faa2194a261c01381f90e65261879985476014a0a37a334593a05eb")
        model = replicate.models.get("22-hours/vintedois-diffusion")
        version = model.versions.get("28cea91bdfced0e2dc7fda466cc0a46501c0edc84905b2120ea02e0707b967fd")
    except Exception as e:
        return "", f"Error while initializing Replicate model: {e}"
    inputs = {
        "prompt": text,
        "width": 512,
        "height": 512,
        "prompt_strength": 0.8,
        "num_outputs": 1,
        "num_inference_steps": 50,
        "guidance_scale": 6,
        "scheduler": "K_EULER_ANCESTRAL",
    }
    try:
        logger.debug(f">>> Replicate request: {text}")
        output = version.predict(**inputs)
        logger.debug(f">>> Replicate response: {output}")
    except Exception as e:
        return "", f"Error while getting image: {e}"
    if isinstance(output, list):
        return output[0] or "", None
    return output or "", None


async def check_stream(user_login: str, chat_id, verb_form: str, vk_group_id=None):
    db_stream_checker = TinyDB('roulette/dbStreamChecker_' + user_login + '.json')
    last_stream_id = -1
    while True:
        try:
            logger.info("Stream checker: running for " + user_login)
            url = 'https://api.twitch.tv/helix/streams?user_login=' + user_login
            game_url = 'https://api.twitch.tv/helix/games?id='
            my_headers = {
                'Client-ID': TWITCH_CLIENT_ID,
                'Authorization': TWITCH_BEARER_TOKEN
            }
            response = requests.get(url, headers=my_headers, timeout=15)
            data = response.json()['data']
            if len(data) != 0 and data[0]['type'] == 'live':
                stream = data[0]
                logger.info("Stream checker: streaming " + user_login)
                stream_id = stream['id']
                if last_stream_id != stream_id:
                    last_stream_id = stream_id
                    username = stream['user_name']
                    #msg = "👾 " + username + " " + verb_form + " стрим! Категория: " + stream[
                    #    'game_name'] + "\nНазвание стрима - " + stream[
                    #           'title'] + "\nhttps://www.twitch.tv/" + user_login
                    msg = "👾 " + username + " " + verb_form + " стрим!\n" + stream['title'] + "\nКатегория: " + stream['game_name'] + "\nhttps://www.twitch.tv/" + user_login
                    #await asyncio.sleep(30)
                    #response = requests.get(url, headers=my_headers, timeout=15)
                    #data = response.json()['data']
                    #stream = data[0]
                    thumbnail = stream['thumbnail_url']
                    game_thumbnail = None
                    #if len(stream['game_id']) != 0 :
                    #    try:
                    #        game = requests.get(game_url + stream['game_id'], headers=my_headers, timeout=15)
                    #        game_data = game.json()['data']
                    #        if len(game_data) != 0:
                    #            game_thumbnail = game_data[0]['box_art_url']
                    #            if game_thumbnail:
                    #                game_thumbnail = game_thumbnail.replace('{width}', '1920').replace('{height}',
                    #                                                                                   '1080')
                    #        if game_thumbnail:
                    #            response_game = requests.get(game_thumbnail, timeout=15)
                    #            for resp in response_game.history:
                    #                if resp.status_code == 302:
                    #                    game_thumbnail = None
                    #        else:
                    #            game_thumbnail = None
                    #    except:
                    #        game_thumbnail = None
                    #        pass
                    #else:
                    #    game_thumbnail = None
                    alert_for_stream_id_showed = db_stream_checker.all()
                    send_msg = True
                    if not alert_for_stream_id_showed:
                        db_stream_checker.insert({"last_stream_id": last_stream_id})
                    else:
                        for showed_stream_id in alert_for_stream_id_showed:
                            if str(last_stream_id) in str(showed_stream_id):
                                send_msg = False
                    if send_msg:
                        mj_response = None
                        mj_error = None
                        #try:
                        #    if 'just chatting' not in stream['game_name'].lower() and 'dota 2' not in stream['game_name'].lower():
                        #        mj_response, mj_error = get_replicate_response('high detailed ' + stream['game_name'] + ', 8k')
                        #except Exception as e:
                        #    logger.error('Stream check failed for ' + user_login + ', mj image failed: ' + str(e))
                        #    pass
                        if mj_error:
                            logger.error('Stream check failed for ' + user_login + ', mj image failed: ' + str(mj_error))
                        logger.info("Stream checker: Send msg " + user_login)
                        db_stream_checker.insert({"last_stream_id": last_stream_id})
                        thumbnail += '?t=' + str(calendar.timegm(time.gmtime()))
                        thumbnail = thumbnail.replace('{width}', '1920').replace('{height}', '1080')
                        game_thumbnail = None
                        if mj_response:
                            try:
                                if vk_group_id is not None:
                                    send_to_vk_wall(user_login, vk_group_id, msg, mj_response)
                                await bot.send_photo(chat_id=chat_id, photo=mj_response, caption=msg)
                            except Exception as e:
                                logger.error('Stream check failed for ' + user_login + ', game image failed: ' + str(e))
                                if vk_group_id is not None:
                                    send_to_vk_wall(user_login, vk_group_id, msg, thumbnail)
                                await bot.send_photo(chat_id=chat_id, photo=thumbnail, caption=msg)
                                pass
                        #elif game_thumbnail:
                        #    try:
                        #        if vk_group_id is not None:
                        #            send_to_vk_wall(user_login, vk_group_id, msg, game_thumbnail)
                        #        await bot.send_photo(chat_id=chat_id, photo=game_thumbnail, caption=msg)
                        #    except Exception as e:
                        #        logger.error('Stream check failed for ' + user_login + ', game iamge failed: ' + str(e))
                        #        if vk_group_id is not None:
                        #            send_to_vk_wall(user_login, vk_group_id, msg, thumbnail)
                        #        await bot.send_photo(chat_id=chat_id, photo=thumbnail, caption=msg)
                        #        pass
                        else:
                            if 'dota 2' in stream['game_name'].lower():
                                thumbnail = 'https://i.imgur.com/zHh83hD.jpg'
                            elif 'just chatting' in stream['game_name'].lower():
                                thumbnail = 'https://i.imgur.com/dUx0Ron.jpg'
                            elif 'StarCraft II' in stream['game_name']:
                                thumbnail = 'https://i.imgur.com/FhOIiOh.jpg'
                            else:
                                thumbnail = 'https://i.imgur.com/NBLskyI.jpg'
                            if vk_group_id is not None:
                                send_to_vk_wall(user_login, vk_group_id, msg, thumbnail)
                            await bot.send_photo(chat_id=chat_id, photo=thumbnail, caption=msg)
                    else:
                        logger.info("Stream checker: Msg already sended " + user_login)
                    await asyncio.sleep(60)
                else:
                    await asyncio.sleep(60)
            else:
                logger.info("Stream checker: Not streaming " + user_login)
                await asyncio.sleep(30)
        except Exception as e:
            logger.error('Stream check failed for ' + user_login + ',: ' + str(e))
            await asyncio.sleep(30)


def send_to_vk_wall(user_login: str, group_id: str, msg: str, photo_url=None):
    try:
        vk = vk_api.VkApi(
            token=os.getenv("VK_APP_TOKEN"))
        upload = VkUpload(vk)
        attachment = []
        if photo_url is not None:
            file_data = requests.get(photo_url).content
            with open(user_login + ".jpg", "wb") as file:
                file.write(file_data)
            photo_list = upload.photo_wall([open(user_login + ".jpg", 'rb')])
            attachment = ','.join('photo{owner_id}_{id}'.format(**item) for item in photo_list)
        vk.method("wall.post", {
            "owner_id": group_id,
            "message": msg,
            "attachments": attachment,
            "copyright": copyright,
            "v": 5.122
        })
    except Exception as e:
        logger.error('Send to vk failed: ' + str(e))


def send_to_vk_wall(user_login: str, group_id: str, msg: str, photo_url=None):
    try:
        vk = vk_api.VkApi(
            token=os.getenv("VK_APP_TOKEN"))
        upload = VkUpload(vk)
        attachment = []
        if photo_url is not None:
            file_data = requests.get(photo_url).content
            with open(user_login + ".jpg", "wb") as file:
                file.write(file_data)
            photo_list = upload.photo_wall([open(user_login + ".jpg", 'rb')])
            attachment = ','.join('photo{owner_id}_{id}'.format(**item) for item in photo_list)
        vk.method("wall.post", {
            "owner_id": group_id,
            "message": msg,
            "attachments": attachment,
            "copyright": copyright,
            "v": 5.122
        })
    except Exception as e:
        logger.error('Send to vk failed: ' + str(e))


async def main():
    # first_task = asyncio.create_task(check_stream('c_a_k_e', os.getenv("CAKE_CHANNEL_ID"), 'завёл', os.getenv("VK_CAKE_GROUP_ID")))
    # second_task = asyncio.create_task(check_stream('nastjadd', os.getenv("NASTJIADD_CHAT_ID"), 'завела'))
    first_task = asyncio.create_task(check_stream('c_a_k_e', os.getenv("CAKE_CHANNEL_ID"), 'завёл', os.getenv("VK_CAKE_GROUP_ID")))
#    third_task = asyncio.create_task(check_stream('ilame', os.getenv("BOT_TEST_ROOM_CHANNEL_ID"), 'завёл'))
    await asyncio.gather(first_task)


asyncio.run(main())

if __name__ == '__main__':
    main()
