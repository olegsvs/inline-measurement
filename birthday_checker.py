import asyncio
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from os.path import exists
import json
import sys
# Enable logging
logging.basicConfig(
    filename=datetime.now().strftime('logs/log_birthday_checker_%d_%m_%Y_%H_%M.log'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
load_dotenv()

# TG_BOT_TOKEN
TOKEN = os.getenv("TG_BOT_TOKEN")
VOLJ_CHILL_CHAT_ID = os.getenv("VOLJ_CHILL_CHAT_ID")
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


async def check_birthday():
    while True:
        try:
            now = datetime.now()
            current_day = str(now.day)
            current_month = str(now.month)
            current_year = now.year
            if len(current_day) == 1:
                current_day = "0" + current_day
            if len(current_month) == 1:
                current_month = "0" + current_month
            logger.info('check_birthday...')
            if exists('roulette/dbBirthdays.json'):
                file = open('roulette/dbBirthdays.json', encoding='utf-8', mode='r+')
                json_file = None
                try:
                    json_file = json.load(file)
                except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error('Birthday load json failed: ' + str(e) + ", line: " + str(exc_tb.tb_lineno))
                if json_file is not None:
                    for user in json_file['users']:
                        last_sent_year: int = -1
                        try:
                            last_sent_year = user['last_sent_in_year']
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error('Birthday last_sent_year failed: ' + str(e) + ", line: " + str(exc_tb.tb_lineno))
                            pass
                        if last_sent_year == 0 or last_sent_year != current_year:
                            nickname = user['username']
                            birthday_date = str(user['birthdate']).split('.')
                            birthday_day = birthday_date[0]
                            birthday_month = birthday_date[1]
                            logger.info('Birthday user: ' + nickname + ' ' + birthday_day + ' ' + birthday_month + ' ' + current_day + ' ' + current_month)
                            if current_month == birthday_month:
                                if current_day == birthday_day:
                                    user['last_sent_in_year'] = int(current_year)
                                    msg = '@' + nickname + ', С Днем Рождения! 🍾🎁🎊🎂🎉🎈🥳'
                                    await bot.send_message(chat_id=VOLJ_CHILL_CHAT_ID, text=msg)
                    file.seek(0)
                    json.dump(json_file, file, indent=4)
                    file.truncate()
                    file.close()
            await asyncio.sleep(60)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error('Birthday check failed: ' + str(e) + ", line: " + str(exc_tb.tb_lineno))
            await asyncio.sleep(60)


def main():
    asyncio.run(check_birthday())


if __name__ == '__main__':
    main()
