import asyncio
import calendar
import logging
import os
import io
import random
import time
import json
import sys
from datetime import datetime
from random import randrange
from uuid import uuid4
import pandas as pd
import requests
from dotenv import load_dotenv
from tinydb import TinyDB, Query
import subprocess
from sys import platform
from lxml import etree
from os.path import exists
import urllib.request
import urllib.parse
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineQuery, InputTextMessageContent, InlineQueryResultArticle, InlineKeyboardMarkup, \
    InlineKeyboardButton, ParseMode, ChatPermissions

# Enable logging
logging.basicConfig(
    filename=datetime.now().strftime('logs/log_%d_%m_%Y_%H_%M.log'),
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
# Init db
db = TinyDB('users/db.json')
dbCBR = TinyDB('users/dbCBR.json')
dbRANDOM = TinyDB('users/dbRANDOM.json')
dbRoulette = TinyDB('roulette/dbRoulette.json')
dbCDRoulette = TinyDB('roulette/dbCDRoulette.json')
UserQuery: Query = Query()
error_template = 'Попробуйте позднее'
error_cbr_template = 'Курс валют временно недоступен, попробуйте позднее'
update_template = 'Обновление в 03:10 MSK'
update_template_rnd = 'Обновление в 03:10 MSK, C_a_k_e chat only'
update_cbr_template = 'Обновление каждый час'
wordle_template = 'Узнай, смог ли сегодня бот решить wordle, обновление в 03:10 MSK'
wordle_filename = 'wordle_screenshot_imgur_link.txt'
wordle_not_solved_filename = 'wordle_not_solved_screenshot_imgur_link.txt'
sad_emoji = ['😒', '☹️', '😣', '🥺', '😞', '🙄', '😟', '😠', '😕', '😖', '😫', '😩', '😰', '😭']
happy_emoji = ['😀', '😏', '😱', '😂', '😁', '😂', '😉', '😊', '😋', '😎', '☺', '😏']


def get_raspberry_info():
    if platform == "linux":
        try:
            rasp_model = subprocess.run(['cat', '/sys/firmware/devicetree/base/model'], capture_output=True,
                                        text=True).stdout.strip("\n")
            temp = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True, text=True).stdout.strip("\n")
            uptime = subprocess.run(['uptime', '-p'], capture_output=True, text=True).stdout.strip("\n")
            return 'Запущено на: ' + rasp_model + ', ' + temp + '\nUptime: ' + uptime
        except:
            return ''
    else:
        return ''


def get_start_text():
    return 'Пожелания: @olegsvs (aka SentryWard)\n' \
           'https://github.com/olegsvs/yepcock-size-bot\n' \
           'Для чата https://t.me/cakestreampage\n' \
           'Бот поддерживает как инлайн режим\n' \
           'Так и команды(для работы команд добавьте бота в группу и назначьте администратором)\n' \
           '/ping, /p - Погладить бота\n' \
           '/weather, /w - Узнать погоду, укажите город после команды\n' \
           '/roulette, /r - Русская рулетка: выживи или получи мут на 25 минут, шанс: количество пуль к 6(при выигрыше +(3 * на количество пуль)(по умолчанию одна пуля, количество пуль можно указать после команды(от 1 до 5 пуль)), при проигрыше -количество пуль в очках) КД 1 час\n' \
           '/duel, /d -  Отправить в ответ на сообщение того, кого хочешь вызвать на дуэль с указанием ставки. Очки проигравшего перейдут к выигрывшему\n' \
           '/midas, /m - Отправить в ответ на сообщение того, кого хочешь замидасить(рулетка на мут на 25 минут, шанс 1 к 3). Стоимость 30 очков\n' \
           '/revive, /rv - Добровольный мут на 25 минут\n' \
           '/points, /ps - Показать количество очков\n' \
           '/top10, /t - Показать топ 10 по очкам\n' \
           '/bottom10, /b - Показать у кого меньше всех очков\n' \
           '' + get_raspberry_info()


def get_info_text():
    return 'Бот поддерживает как инлайн режим\n' \
           'Так и команды(для работы команд добавьте бота в группу и назначьте администратором)\n' \
           '/ping, /p - Погладить бота\n' \
           '/weather, /w - Узнать погоду, укажите город после команды\n' \
           '/roulette, /r - Русская рулетка: выживи или получи мут на 25 минут, шанс: количество пуль к 6(при выигрыше +(3 очка * на количество пуль)(по умолчанию одна пуля, количество пуль можно указать после команды(от 1 до 5 пуль)), при проигрыше -количество пуль в очках) КД 1 час\n' \
           '/duel, /d -  Отправить в ответ на сообщение того, кого хочешь вызвать на дуэль с указанием ставки. Очки проигравшего перейдут к выигрывшему\n' \
           '/midas, /m - Отправить в ответ на сообщение того, кого хочешь замидасить(рулетка на мут на 25 минут, шанс 1 к 3). Стоимость 30 очков\n' \
           '/revive, /rv - Добровольный мут на 25 минут\n' \
           '/points, /ps - Показать количество очков\n' \
           '/top10, /t - Показать топ 10 по очкам\n' \
           '/bottom10, /b - Показать у кого меньше всех очков\n'


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    key_board = [
        [InlineKeyboardButton('НАЧАТЬ', switch_inline_query_current_chat='')],
    ]

    try:
        bot_message = await message.reply(get_start_text(),
                                          reply_markup=InlineKeyboardMarkup(inline_keyboard=key_board))
        await asyncio.sleep(20)
        await bot_message.delete()
        await message.delete()
    except Exception as e:
        logger.error('Failed start: ' + str(e))


def sizer_cock(userId):
    size = sync_with_db(userId, "sizer_cock", randrange(30))
    if size >= 15:
        emoji = random.choice(happy_emoji)
    else:
        emoji = random.choice(sad_emoji)
    text = 'Мой кок размером: <b>%s' % size + 'см</b> ' + emoji
    return text


def homo_sexual(userId):
    percent = sync_with_db(userId, "homo_sexual", randrange(101))
    type = sync_with_db(userId, "homo_type", random.choice(["актив", "пассив"]))
    text = "Я на <b>%s</b>" % percent + "<b>%</b>" + " гомосексуал, " + type + " (LGBT) 🏳️‍🌈"
    return text


def iq_test(userId):
    iq = sync_with_db(userId, "iq_test", randrange(161))
    if iq >= 100:
        emoji = random.choice(happy_emoji)
    else:
        emoji = random.choice(sad_emoji)
    hint = ''
    if iq > 140:
        hint = 'такой показатель всего у 0,2% человечества'
    if iq <= 140:
        hint = 'такой показатель всего у 2,5% человечества'
    if iq <= 130:
        hint = 'очень высокий'
    if iq <= 120:
        hint = 'высокий'
    if iq <= 110:
        hint = 'выше среднего'
    if iq <= 100:
        hint = 'средний'
    if iq <= 90:
        hint = 'ниже среднего'
    if iq <= 80:
        hint = 'как у приматов'
    if iq <= 76:
        hint = 'как у китов'
    if iq <= 72:
        hint = 'как у слонов'
    if iq <= 68:
        hint = 'как у собак'
    if iq <= 64:
        hint = 'как у кошек'
    if iq <= 60:
        hint = 'как у крысок'
    if iq <= 56:
        hint = 'как у свинок'
    if iq <= 52:
        hint = 'как у белок'
    if iq <= 48:
        hint = 'как у соек'
    if iq <= 44:
        hint = 'как у ворон'
    if iq <= 40:
        hint = 'как у енотов'
    if iq <= 36:
        hint = 'как у морских котиков'
    if iq <= 32:
        hint = 'как у попугаев'
    if iq <= 28:
        hint = 'как у лошадей'
    if iq <= 24:
        hint = 'как у голубей'
    if iq <= 20:
        hint = 'как у овец'
    if iq <= 16:
        hint = 'как у крокодилов'
    if iq <= 12:
        hint = 'как у пчёл'
    if iq <= 8:
        hint = 'как у черепах'
    if iq <= 4:
        hint = 'как у пыли'

    text = 'Мой IQ: <b>%s' % iq + '</b> из 160 баллов, ' + hint + ' ' + emoji
    return text


key_get_my_cock_result = [
    [InlineKeyboardButton('Узнай свой размер 👉👈', switch_inline_query_current_chat='')],
]

key_daily_result = [
    [InlineKeyboardButton('Узнай свои данные 👉👈 🏳️‍🌈 🧠', switch_inline_query_current_chat='')],
]

key_get_my_IQ_result = [
    [InlineKeyboardButton('Проверь свой интеллект 🧠', switch_inline_query_current_chat='')],
]

key_get_my_gay_result = [
    [InlineKeyboardButton('Узнай свои шансы 🏳️‍🌈', switch_inline_query_current_chat='')],
]


def random_gay():
    user_text = get_random_gay_user_from_csv()
    text = '🎉 Сегодня ГЕЙ 🌈 дня - ' + user_text
    return text


def random_beautiful():
    user_text = get_random_beautiful_user_from_csv()
    text = '🎉 Сегодня КРАСАВЧИК 😊 дня - ' + user_text
    return text


def random_couple():
    user1_text = get_random_couple_user_from_csv(is_first=True)
    user2_text = get_random_couple_user_from_csv(is_first=False)
    text = '🎉 Сегодня ПАРА 😳 дня - ' + user1_text + ' и ' + user2_text + ' 💕'
    return text


@dp.chosen_inline_handler()
async def on_result_chosen(message: types.Message):
    logger.info(message)
    logger.info('\n')


def get_inline_id(prefix: str):
    return prefix + '_' + str(uuid4())


@dp.inline_handler()
async def inlinequery(inline_query: InlineQuery):
    logger.info(inline_query)
    results = [
        InlineQueryResultArticle(
            id=get_inline_id('sizer_cock'),
            title="Дейли инфо...",
            description=update_template,
            thumb_url='https://i.imgur.com/UxWJh8V.png',
            input_message_content=InputTextMessageContent(sizer_cock(inline_query.from_user.id)
                                                          + '\n' + homo_sexual(inline_query.from_user.id)
                                                          + '\n' + iq_test(inline_query.from_user.id),
                                                          parse_mode=ParseMode.HTML),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=key_daily_result)
        ),
        InlineQueryResultArticle(
            id=get_inline_id('sizer_cock'),
            title="Размер члена...",
            description=update_template,
            thumb_url='https://i.imgur.com/wnV4Le9.png',
            input_message_content=InputTextMessageContent(sizer_cock(inline_query.from_user.id),
                                                          parse_mode=ParseMode.HTML),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=key_get_my_cock_result)
        ),
        InlineQueryResultArticle(
            id=get_inline_id('homo_sexual'),
            title="Я гомосексуал на...",
            description=update_template,
            thumb_url='https://i.imgur.com/1yqokVW.png',
            input_message_content=InputTextMessageContent(homo_sexual(inline_query.from_user.id),
                                                          parse_mode=ParseMode.HTML),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=key_get_my_gay_result)
        ),
        InlineQueryResultArticle(
            id=get_inline_id('iq_test'),
            title="Мой IQ...",
            description=update_template,
            thumb_url='https://i.imgur.com/95qsO7Y.png',
            input_message_content=InputTextMessageContent(iq_test(inline_query.from_user.id),
                                                          parse_mode=ParseMode.HTML),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=key_get_my_IQ_result)
        ),
        InlineQueryResultArticle(
            id=get_inline_id('random_rollcall'),
            title="Перекличка дня...",
            description=update_template,
            thumb_url='https://i.imgur.com/gpiM7LN.png',
            input_message_content=InputTextMessageContent(random_rollcall(),
                                                          parse_mode=ParseMode.HTML)
        ),
        InlineQueryResultArticle(
            id=get_inline_id('random_couple'),
            title="Пара дня это...",
            description=update_template_rnd,
            thumb_url='https://i.imgur.com/woBmbIn.png',
            input_message_content=InputTextMessageContent(random_couple(),
                                                          parse_mode=ParseMode.HTML)
        ),
        InlineQueryResultArticle(
            id=get_inline_id('random_gay'),
            title="Гей дня это...",
            description=update_template_rnd,
            thumb_url='https://i.imgur.com/0OCN8kR.png',
            input_message_content=InputTextMessageContent(random_gay(),
                                                          parse_mode=ParseMode.HTML)
        ),
        InlineQueryResultArticle(
            id=get_inline_id('random_beautiful'),
            title="Красавчик дня это...",
            description=update_template_rnd,
            thumb_url='https://i.imgur.com/YoLgEiP.png',
            input_message_content=InputTextMessageContent(random_beautiful(),
                                                          parse_mode=ParseMode.HTML)
        ),
        InlineQueryResultArticle(
            id=get_inline_id('get_exchange_rates'),
            title="Курс ЦБ РФ $/€ к ₽",
            description=update_cbr_template,
            thumb_url='https://image.flaticon.com/icons/png/512/893/893078.png',
            input_message_content=InputTextMessageContent(get_exchange_rates(),
                                                          parse_mode=ParseMode.HTML),
        ),
        InlineQueryResultArticle(
            id=get_inline_id('info_text'),
            title="О боте",
            description='Описание',
            thumb_url='https://i.imgur.com/gRBXXvn.png',
            input_message_content=InputTextMessageContent(get_info_text(),
                                                          parse_mode=ParseMode.HTML, disable_web_page_preview=True),
        ),
    ]

    results.insert(1, get_wordle_result()[0])
    try:
        await bot.answer_inline_query(inline_query.id, results=results, cache_time=1)
        logger.info('\n')
    except Exception as e:
        logger.error('Failed to update.inline_query.answer: ' + str(e))
        logger.info('\n')


def get_wordle_result():
    answer = []
    if exists(wordle_filename):
        wordle_link = io.open(wordle_filename, encoding='utf-8').read()
        answer.append(InlineQueryResultArticle(
            id=get_inline_id('wordle_solved'),
            title="Wordle...",
            description=wordle_template,
            thumb_url='https://i.imgur.com/KMrshXL.png',
            input_message_content=InputTextMessageContent(
                'Сегодня бот смог отгадать слово 😎!\r\nПопытка была {} MSK\r\nСможешь доказать, что кожаные мешки лучше?\r\n<a href="{}">&#8204;</a>\r\nОтгадай слово '
                'на https://wordle.belousov.one'
                    .format(get_formatted_date(os.path.getctime(wordle_filename)),
                            wordle_link), parse_mode=ParseMode.HTML),
        ))
    else:
        if exists(wordle_not_solved_filename):
            wordle_link = io.open(wordle_not_solved_filename, encoding='utf-8').read()
            answer.append(InlineQueryResultArticle(
                id=get_inline_id('wordle_solved'),
                title="Wordle...",
                description=wordle_template,
                thumb_url='https://i.imgur.com/KMrshXL.png',
                input_message_content=InputTextMessageContent(
                    'Сегодня бот не смог отгадать слово {}\r\nПопытка была {} MSK\r\nКожаные мешки заскамили малютку(\r\n<a href="{}">&#8204;</a>\r\nОтгадай '
                    'слово на https://wordle.belousov.one'
                        .format(random.choice(sad_emoji),
                                get_formatted_date(os.path.getctime(wordle_not_solved_filename)), wordle_link),
                    parse_mode=ParseMode.HTML),
            ))
        else:
            answer.append(InlineQueryResultArticle(
                id=get_inline_id('wordle_unsolved'),
                title="Wordle...",
                description=wordle_template,
                thumb_url='https://i.imgur.com/KMrshXL.png',
                input_message_content=InputTextMessageContent(
                    'Бот ещё не решил wordle\r\nОтгадайте слово на https://wordle.belousov.one',
                    parse_mode=ParseMode.HTML),
            ))
    return answer


def random_rollcall():
    try:
        old_rollcall_of_the_day = dbRANDOM.search(Query().old_rollcall_of_the_day.exists())
        if not old_rollcall_of_the_day:
            lines = io.open('phrases.txt', encoding='utf-8').read().splitlines()
            choice = random.choice(lines)
            dbRANDOM.insert({'old_rollcall_of_the_day': str(choice)})
            return choice
        else:
            return old_rollcall_of_the_day[0]['old_rollcall_of_the_day']
    except Exception as e:
        logger.error('Failed to random_rollcall: ' + str(e))
        return error_template


def get_exchange_rates():
    try:
        old_data_usd = dbCBR.search(Query().cbrUSD.exists())
        old_data_eur = dbCBR.search(Query().cbrEUR.exists())
        last_timestamp = dbCBR.search(Query().cbrTS.exists())
        now_ts = calendar.timegm(time.gmtime())
        logger.info('get_exchange: now_ts:'f"{now_ts=}")

        if not last_timestamp:
            need_force_update = True
        else:
            diff = now_ts - last_timestamp[0]['cbrTS']
            logger.info('get_exchange: diff:'f"{diff=}")
            if diff >= 3600:
                need_force_update = True
            else:
                need_force_update = False

        if need_force_update:
            old_data_eur = None
            old_data_usd = None

        if not old_data_usd:
            logger.info('get_exchange: old_data_usd not found, update from cbr-xml-daily...')
            upd_ts = get_formatted_date(now_ts)
            xml_response = etree.fromstring(
                requests.get("http://www.cbr.ru/scripts/XML_daily.asp", timeout=2).text.encode("1251"))
            USD = xml_response.find("Valute[@ID='R01235']/Value").text
            EUR = xml_response.find("Valute[@ID='R01239']/Value").text
            dbCBR.drop_tables()
            dbCBR.insert({'cbrUSD': USD})
            dbCBR.insert({'cbrEUR': EUR})
            dbCBR.insert({'cbrTS': now_ts})
            return get_exchange_text(upd_ts, USD, EUR)
        else:
            logger.info('get_exchange: old_data_usd found')
            upd_ts = get_formatted_date(last_timestamp[0]['cbrTS'])
            return get_exchange_text(upd_ts, old_data_usd[0]['cbrUSD'], old_data_eur[0]['cbrEUR'])
    except Exception as e:
        logger.error('Failed to get_exchange_rates: ' + str(e))
        return error_cbr_template


def get_exchange_text(upd_ts, usd, eur):
    text = "Обновлено %s MSK" % upd_ts + "\n" \
                                         "USD: <b>%s</b>" % usd + " ₽\n" \
                                                                  "EUR: <b>%s</b>" % eur + " ₽\n" \
                                                                                           "Инфо от ЦБ РФ"
    return text


def get_formatted_date(timestamp):
    date_time = datetime.fromtimestamp(timestamp)
    return date_time.strftime("%d.%m.%Y, %H:%M:%S")


# noinspection PyTypeChecker
def sync_with_db(userId, varType, varValue):
    user = db.search(UserQuery.id == userId)
    logger.info('sync_with_db:'f" {user=} "f" {userId=} "f" {varType=} "f" {varValue=} ")
    if not user:
        logger.info('sync_with_db: user not found')
        db.insert({'id': userId, varType: varValue})
        return varValue
    else:
        userByVarType = db.search((UserQuery.id == userId) & (UserQuery[varType].exists()))
        logger.info('sync_with_db: userByVarType:'f"{userByVarType=}")
        if not userByVarType:
            logger.info('sync_with_db: userByVarType none, update value...')
            db.update({'id': userId, varType: varValue}, UserQuery.id == userId)
            return varValue
        else:
            logger.info('sync_with_db: userByVarType exists, get value...')
            return user[0][varType]


async def is_old_message(message: types.Message):
    now_ts = calendar.timegm(time.gmtime())
    logger.info(
        "Check is old message, msg ts : " + str(round(message.date.timestamp())) + " now ts: " + str(round(now_ts)))
    if round(message.date.timestamp() + 300) < round(now_ts):
        logger.info("Check is old message, deleting")
        await message.delete()
        return True
    else:
        logger.info("Check is old message, is now message")
        return False


@dp.message_handler(commands=['info', 'i'])
async def info(message: types.Message):
    logger.info("info request")
    try:
        if await is_old_message(message):
            return
        bot_message = await message.reply(get_info_text(), disable_web_page_preview=True)
        await asyncio.sleep(20)
        await bot_message.delete()
        await message.delete()
    except Exception as e:
        logger.error('Failed info: ' + str(e))


@dp.message_handler(commands=['ping', 'p'])
async def ping(message: types.Message):
    logger.info("ping request")
    try:
        if await is_old_message(message):
            return
        bot_message = await message.reply('pong')
        await asyncio.sleep(3)
        await message.delete()
        await bot_message.delete()
    except Exception as e:
        logger.error('Failed ping: ' + str(e))


def get_random_gay_user_from_csv():
    try:
        old_user_id = dbRANDOM.search(Query().gay_id.exists())
        old_user_name = dbRANDOM.search(Query().gay_name.exists())

        if not old_user_id:
            logger.info('get_random_gay: old_user_id not found, get random...')
            df = pd.read_csv('members.csv', delimiter=",", lineterminator="\n")
            random_user = df.sample()
            user_id = random_user.get('user id').to_numpy()
            user_name1 = random_user.get('username').to_numpy()
            # user_name2 = random_user.get('name').to_numpy()
            logger.info('get_random_gay: UserName:'f"{user_name1[0]=}")  # f"{user_name2=}")
            # if is_nan(user_name1):
            #     user_name = user_name2[0]
            # else:
            #     user_name = user_name1[0]
            user_name = user_name1[0]
            logger.info('get_random_gay: Random user:'f"{user_id[0]=}"f"{user_name=}")
            dbRANDOM.insert({'gay_id': int(user_id[0])})
            dbRANDOM.insert({'gay_name': str(user_name)})
            return get_user_link_text(user_id[0], user_name)
        else:
            logger.info('get_random_gay: old_user_id found')
            return get_user_link_text(old_user_id[0]['gay_id'], old_user_name[0]['gay_name'])
    except Exception as e:
        logger.error('Failed to get_random_gay_user_from_csv: ' + str(e))
        return error_template


def get_user_link_text(user_id, user_name):
    text = '<a href="tg://user?id=%s' % user_id + '">@%s' % user_name + '</a>'
    logger.info('get_user_link_text: 'f"{text=}")
    return text


def is_nan(num):
    return num != num


def get_random_couple_user_from_csv(is_first: bool):
    try:
        if is_first:
            old_user_id = dbRANDOM.search(Query().couple_first_id.exists())
            old_user_name = dbRANDOM.search(Query().couple_first_name.exists())
        else:
            old_user_id = dbRANDOM.search(Query().couple_second_id.exists())
            old_user_name = dbRANDOM.search(Query().couple_second_name.exists())

        if not old_user_id:
            logger.info('get_random_couple: old_user_id not found, get random...')
            df = pd.read_csv('members.csv', delimiter=",", lineterminator="\n")
            random_user = df.sample()
            user_id = random_user.get('user id').to_numpy()
            user_name1 = random_user.get('username').to_numpy()
            logger.info('get_random_couple: UserName:'f"{user_name1[0]=}")
            user_name = user_name1[0]
            logger.info('get_random_couple: Random user:'f"{user_id[0]=}"f"{user_name=}")
            if is_first:
                dbRANDOM.insert({'couple_first_id': int(user_id[0])})
                dbRANDOM.insert({'couple_first_name': str(user_name)})
            else:
                dbRANDOM.insert({'couple_second_id': int(user_id[0])})
                dbRANDOM.insert({'couple_second_name': str(user_name)})
            return get_user_link_text(user_id[0], user_name)
        else:
            logger.info('get_random_couple: old_user_id found')
            if is_first:
                return get_user_link_text(old_user_id[0]['couple_first_id'],
                                          old_user_name[0]['couple_first_name'])
            else:
                return get_user_link_text(old_user_id[0]['couple_second_id'],
                                          old_user_name[0]['couple_second_name'])
    except Exception as e:
        logger.error('Failed to get_random_couple_user_from_csv: ' + str(e))
        return error_template


def get_random_beautiful_user_from_csv():
    try:
        old_user_id = dbRANDOM.search(Query().beautiful_id.exists())
        old_user_name = dbRANDOM.search(Query().beautiful_name.exists())

        if not old_user_id:
            logger.info('get_random_beautiful: old_user_id not found, get random...')
            df = pd.read_csv('members.csv', delimiter=",", lineterminator="\n")
            random_user = df.sample()
            user_id = random_user.get('user id').to_numpy()
            user_name1 = random_user.get('username').to_numpy()
            logger.info('get_random_beautiful: UserName:'f"{user_name1[0]=}")
            user_name = user_name1[0]
            logger.info('get_random_beautiful: Random user:'f"{user_id[0]=}"f"{user_name=}")
            dbRANDOM.insert({'beautiful_id': int(user_id[0])})
            dbRANDOM.insert({'beautiful_name': str(user_name)})
            return get_user_link_text(user_id[0], user_name)
        else:
            logger.info('get_random_beautiful: old_user_id found')
            return get_user_link_text(old_user_id[0]['beautiful_id'], old_user_name[0]['beautiful_name'])
    except Exception as e:
        logger.error('Failed to get_random_beautiful_user_from_csv: ' + str(e))
        return error_template


@dp.message_handler(commands=['roulette', 'r'])
async def roulette(message: types.Message):
    logger.info("roulette request")
    try:
        if await is_old_message(message):
            return
        await message.delete()
        logger.info("Roulette: orig message: " + str(message.text))

        last_global_timestamp = dbCDRoulette.all()
        now_ts = calendar.timegm(time.gmtime())
        logger.info('roulette: global ts check, now_ts:'f"{now_ts=}")
        if not last_global_timestamp:
            dbCDRoulette.insert({'ts': int(time.time())})
        else:
            logger.info(str(last_global_timestamp))
            diff = now_ts - last_global_timestamp[0]['ts']
            logger.info('roulette: global time diff:'f"{diff=}")
            if diff >= 10:
                dbCDRoulette.update({'ts': int(time.time())})
            else:
                bot_message = await message.answer(
                    message.from_user.get_mention(
                        as_html=True) + ", револьвер перегрелся, попробуйте через 10 секунд ⏳",
                    parse_mode=ParseMode.HTML)
                logger.info("Roulette, send message: " + str(bot_message.text))
                await asyncio.sleep(10)
                await bot_message.delete()
                return

        bullets_count_raw = message.get_args().strip()
        logger.info("Roulette: bullets_count_raw: " + str(bullets_count_raw))
        bullets_count = 1
        if bullets_count_raw.isdigit() and (1 <= int(bullets_count_raw) <= 5):
            bullets_count = int(bullets_count_raw)
        logger.info("Roulette: bullets_count: " + str(bullets_count))
        logger.info(
            "Roulette request: from: " + str(message.from_user.mention) + ", chat_name: " + str(
                message.chat.title) + ", chat_id: " + str(
                message.chat.id))
        user_id = message.from_user.id
        member = await message.chat.get_member(user_id)
        logger.info("Roulette: member status: " + member.status)
        if member.status == 'member' or member.status == 'left' or member.status == 'restricted' or member.status == 'kicked':
            last_timestamp = dbRoulette.search(UserQuery.id == user_id)
            now_ts = calendar.timegm(time.gmtime())
            logger.info('roulette: now_ts:'f"{now_ts=}")
            allow_roulette = False
            next_roll_minutes = 0
            next_roll_seconds = 0
            new_user = False
            points = 0
            if not last_timestamp:
                allow_roulette = True
                new_user = True
            else:
                diff = now_ts - last_timestamp[0]['ts']
                points = last_timestamp[0]['points']
                logger.info('roulette: time diff:'f"{diff=}")
                if diff >= 3600:
                    allow_roulette = True
                    new_user = False
                else:
                    next_roll_time = 3600 - diff
                    next_roll_minutes = str((next_roll_time % 3600) // 60)
                    next_roll_seconds = str((next_roll_time % 3600) % 60)
                    allow_roulette = False
            if allow_roulette:
                bot_message_1 = await message.answer(
                    "💥 " + message.from_user.get_mention(as_html=True) + " решает сыграть в русскую рулетку с " + str(
                        bullets_count) + str(
                        numeral_noun_declension(bullets_count, " пулей", " пулями",
                                                " пулями")) + " из 6 в барабане! 😱",
                    parse_mode=ParseMode.HTML)
                logger.info("Roulette, send message: " + str(bot_message_1.text))
                dice = None
                bot_message_2 = None
                kill = False
                if bullets_count == 1:
                    dice = await bot.send_dice(chat_id=message.chat.id)
                    logger.info("Roulette, random from dice is: " + str(dice.dice.value))
                    kill = dice.dice.value == 1
                    await asyncio.sleep(10)
                elif bullets_count == 5:
                    dice = await bot.send_dice(chat_id=message.chat.id)
                    logger.info("Roulette, random from dice is: " + str(dice.dice.value))
                    kill = dice.dice.value != 6
                    await asyncio.sleep(10)
                else:
                    bot_message_2 = await message.answer_sticker(
                        sticker='CAACAgIAAxkBAAEFmrNi_1NSWAwgsAVvrxM5luDs53IfSgACZx4AAh9h-EumIi-Hcwnw1SkE')
                    rand = random.randint(1, 6)
                    logger.info("Roulette, random is: " + str(rand))
                    if bullets_count == 4:
                        if rand <= 4:
                            kill = True
                    if bullets_count == 3:
                        if rand <= 3:
                            kill = True
                    if bullets_count == 2:
                        if rand <= 2:
                            kill = True
                    logger.info("Roulette, send message: " + str(bot_message_2.text))
                    await asyncio.sleep(5)
                logger.info("Roulette, kill is: " + str(kill))
                if kill:
                    until_date = (int(time.time()) + 1500)
                    try:
                        if new_user:
                            new_points = 0
                            dbRoulette.insert({'id': user_id, 'ts': int(time.time()), 'points': 0,
                                               'user_mention': message.from_user.mention.replace('@', '')})
                        else:
                            new_points = points - bullets_count
                            dbRoulette.update({'id': user_id, 'ts': int(time.time()), 'points': new_points},
                                              UserQuery.id == user_id)
                        await message.chat.restrict(message.from_user.id,
                                                    ChatPermissions(can_send_messages=False),
                                                    until_date=until_date)
                        bot_message = await message.answer(
                            "💥 " + get_dead_quote(
                                message.from_user.get_mention(as_html=True)) + " 🔫😎\nРеспаун через 25 минут. -" + str(
                                bullets_count) + " " + str(
                                numeral_noun_declension(bullets_count, "очко", "очка", "очков")) + ", баланс: " + str(
                                new_points) + " " + random.choice(
                                sad_emoji), parse_mode=ParseMode.HTML)
                        logger.info("Roulette, send message: " + str(bot_message.text))
                        if dice is not None:
                            await dice.delete()
                        if bot_message_1 is not None:
                            await bot_message_1.delete()
                        if bot_message_2 is not None:
                            await bot_message_2.delete()
                        await asyncio.sleep(1500)
                        await bot_message.delete()
                    except Exception as e:
                        if dice is not None:
                            await dice.delete()
                        if bot_message_1 is not None:
                            await bot_message_1.delete()
                        if bot_message_2 is not None:
                            await bot_message_2.delete()
                        logger.error('Failed roulette kill: ' + str(e))
                        bot_message = await message.answer(
                            message.from_user.get_mention(as_html=True) + ", админы неуязвимы для рулетки 😭",
                            parse_mode=ParseMode.HTML)
                        logger.info("Roulette, send message: " + str(bot_message.text))
                        await asyncio.sleep(3)
                        await bot_message.delete()
                else:
                    add_points = 3 * bullets_count
                    if new_user:
                        new_points = add_points
                        dbRoulette.insert({'id': user_id, 'ts': int(time.time()), 'points': new_points,
                                           'user_mention': message.from_user.full_name})
                    else:
                        new_points = points + add_points
                        dbRoulette.update({'id': user_id, 'ts': int(time.time()), 'points': new_points},
                                          UserQuery.id == user_id)
                    bot_message = await message.answer(
                        "💥 " + get_pog_quote(
                            message.from_user.get_mention(as_html=True)) + ". Выиграл(а) в русскую рулетку с " + str(
                            bullets_count) + str(
                            numeral_noun_declension(bullets_count, " пулей", " пулями",
                                                    " пулями")) + " из 6 в барабане! +" + str(add_points) + " " + str(
                            numeral_noun_declension(add_points, "очко", "очка", "очков")) + ", баланс: " + str(
                            new_points) + " " + random.choice(
                            happy_emoji),
                        parse_mode=ParseMode.HTML)
                    logger.info("Roulette, send message: " + str(bot_message.text))
                    if dice is not None:
                        await dice.delete()
                    if bot_message_1 is not None:
                        await bot_message_1.delete()
                    if bot_message_2 is not None:
                        await bot_message_2.delete()
                    await asyncio.sleep(1500)
                    await bot_message.delete()
            else:
                bot_message = await message.answer(
                    message.from_user.get_mention(as_html=True) + ", рулетка перезаряжается, ещё " + str(
                        next_roll_minutes) + " минут и " + str(next_roll_seconds) + " секунд ⏳",
                    parse_mode=ParseMode.HTML)
                logger.info("Roulette, send message: " + str(bot_message.text))
                await asyncio.sleep(3)
                await bot.delete_message(chat_id=bot_message.chat.id, message_id=bot_message.message_id)
        else:
            bot_message = await message.answer(
                message.from_user.get_mention(as_html=True) + ", админы неуязвимы для рулетки 😭",
                parse_mode=ParseMode.HTML)
            await asyncio.sleep(3)
            await bot_message.delete()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('Failed roulette: ' + str(e) + ", line: " + str(exc_tb.tb_lineno))


@dp.message_handler(commands=['midas', 'm'])
async def midas(message: types.Message):
    logger.info("midas request")
    try:
        if await is_old_message(message):
            return
        await message.delete()
        logger.info("Midas: orig message: " + str(message.text))
        logger.info(
            "Midas request: from: " + str(message.from_user.mention) + ", chat_name: " + str(
                message.chat.title) + ", chat_id: " + str(
                message.chat.id))
        if not message.reply_to_message:
            bot_m = await message.answer(
                message.from_user.get_mention(as_html=True) + ", не выбрано сообщение для мидаса",
                parse_mode=ParseMode.HTML)
            logger.info("Midas, send message: " + str(bot_m.text))
            await asyncio.sleep(10)
            await bot_m.delete()
            return
        if message.reply_to_message.from_user.is_bot:
            bot_m = await message.answer(
                message.from_user.get_mention(as_html=True) + ", боты неуязвимы для мидаса 😎",
                parse_mode=ParseMode.HTML)
            logger.info("Midas, send message: " + str(bot_m.text))
            await asyncio.sleep(10)
            await bot_m.delete()
            return
        logger.info("midas request")
        user_id = message.from_user.id
        midas_member = await message.chat.get_member(message.reply_to_message.from_user.id)
        logger.info("midas: member status: " + midas_member.status)
        if midas_member.status == 'member' or midas_member.status == 'restricted':
            last_timestamp = dbRoulette.search(UserQuery.id == user_id)
            allow_midas = False
            midas_points = 0
            if not last_timestamp:
                allow_midas = False
                dbRoulette.insert({'id': user_id, 'points': 0, 'ts': int(time.time()) - 9000,
                                   'user_mention': message.from_user.full_name})
            else:
                midas_points = last_timestamp[0]['points']
                logger.info('midas: points:'f"{midas_points=}")
                if midas_points >= 30:
                    allow_midas = True
                    midas_points = midas_points - 30
                    dbRoulette.update({'id': user_id, 'points': midas_points}, UserQuery.id == user_id)
                else:
                    allow_midas = False
            if allow_midas:
                kill = random.randrange(3)
                logger.info("Midas, random is: " + str(kill))
                if kill == 0:
                    until_date = (int(time.time()) + 1500)
                    try:
                        await message.chat.restrict(message.reply_to_message.from_user.id,
                                                    ChatPermissions(can_send_messages=False),
                                                    until_date=until_date)
                        bot_message = await message.answer(
                            "💥 " + message.from_user.get_mention(
                                as_html=True) + " успешно замидасил(а) " + message.reply_to_message.from_user.get_mention(
                                as_html=True) + " 🔫😎 на 25 минут " + random.choice(
                                sad_emoji) + " +2 очка, баланс: " + str(midas_points + 2), parse_mode=ParseMode.HTML)
                        dbRoulette.update({'id': user_id, 'points': midas_points + 2}, UserQuery.id == user_id)
                        logger.info("Midas, send message: " + str(bot_message.text))
                        await asyncio.sleep(1500)
                        await bot_message.delete()
                    except Exception as e:
                        logger.error('Failed roulette kill: ' + str(e))
                        bot_message = await message.answer(
                            message.from_user.get_mention(as_html=True) + ", админы неуязвимы для мидаса 😭",
                            parse_mode=ParseMode.HTML)
                        logger.info("Midas, send message: " + str(bot_message.text))
                        await asyncio.sleep(3)
                        await bot_message.delete()
                else:
                    user_to_midas_id = message.reply_to_message.from_user.id
                    user_to_midas = dbRoulette.search(UserQuery.id == user_to_midas_id)
                    user_to_midas_points = 0
                    if not user_to_midas:
                        user_to_midas_points = 15
                        dbRoulette.insert(
                            {'id': user_to_midas_id, 'points': user_to_midas_points, 'ts': int(time.time()) - 9000,
                             'user_mention': message.reply_to_message.from_user.full_name})
                    else:
                        user_to_midas_points = user_to_midas[0]['points']
                        logger.info('midas: to midas points:'f"{midas_points=}")
                        user_to_midas_points = user_to_midas_points + 15
                        dbRoulette.update({'id': user_to_midas_id, 'points': user_to_midas_points},
                                          UserQuery.id == user_to_midas_id)
                    bot_message = await message.answer(
                        "💥 " + message.from_user.get_mention(
                            as_html=True) + " хотел(а) замидасить " + message.reply_to_message.from_user.get_mention(
                            as_html=True) + "(+15 очков, баланс: " + str(
                            user_to_midas_points) + ")" + ", но попытка провалилась. -30, баланс: " + str(
                            midas_points) + " " + random.choice(
                            happy_emoji), parse_mode=ParseMode.HTML)
                    logger.info("Midas, send message: " + str(bot_message.text))
                    await asyncio.sleep(1500)
                    await bot_message.delete()
            else:
                bot_message = await message.answer(
                    message.from_user.get_mention(as_html=True) + ", у вас недостаточно очков для мидаса(" + str(
                        midas_points) + "). Необходимо минимум 30.", parse_mode=ParseMode.HTML)
                logger.info("Midas, send message: " + str(bot_message.text))
                await asyncio.sleep(3)
                await bot_message.delete()
        else:
            if midas_member.status == 'left':
                bot_message = await message.answer(
                    message.from_user.get_mention(as_html=True) + ", пользователя нет в чате, его нельзя замидасить",
                    parse_mode=ParseMode.HTML)
                logger.info("Midas, send message: " + str(bot_message.text))
                await asyncio.sleep(3)
                await bot_message.delete()
            elif midas_member.status == 'kicked':
                bot_message = await message.answer(
                    message.from_user.get_mention(as_html=True) + ", , пользователя нет в чате, его нельзя замидасить",
                    parse_mode=ParseMode.HTML)
                logger.info("Midas, send message: " + str(bot_message.text))
                await asyncio.sleep(3)
                await bot_message.delete()
            else:
                bot_message = await message.answer(
                    message.from_user.get_mention(as_html=True) + ", админы неуязвимы для мидаса 😭",
                    parse_mode=ParseMode.HTML)
                logger.info("Midas, send message: " + str(bot_message.text))
                await asyncio.sleep(3)
                await bot_message.delete()

    except Exception as e:
        logger.error('Failed midas: ' + str(e))


@dp.message_handler(commands=['weather', 'w'])
async def weather(message: types.Message):
    logger.info("weather request")
    try:
        if await is_old_message(message):
            return
        city = message.get_args().strip()
        if not city or len(city) == 0:
            bot_message = await message.reply(
                "Укажите населённый пункт, пример: <code>/weather Moscow</code>",
                parse_mode=ParseMode.HTML,
            )
            await asyncio.sleep(3)
            await message.delete()
            await bot.delete_message(chat_id=bot_message.chat.id, message_id=bot_message.message_id)
        else:
            file_url = "https://wttr.in/" + urllib.parse.quote(city.capitalize() + "_transparency=255_0tp_lang=ru.png")
            logger.info('Weather, city: ' + city + ", url: " + file_url)
            urllib.request.urlretrieve(file_url, "weather.jpg")

            text_location = "Местоположение не определено"
            try:
                request = requests.get(url="https://wttr.in/" + urllib.parse.quote(city.capitalize()), timeout=5)
                text_1_index = request.text.find('Location: ')
                logger.info("Weather, find location text, index_1: " + str(text_1_index))
                text_2_index = request.text.rfind('[')
                logger.info("Weather, find location text, index_2: " + str(text_2_index))
                text_location = request.text[text_1_index:text_2_index].replace('Location: ', '')
                text_3_index = text_location.find(' [')
                logger.info("Weather, find location text, index_3: " + str(text_3_index))
                text_location = "Местоположение: " + text_location[0:text_3_index]
                logger.info("Weather, find location text, found location: " + str(text_location))
            except Exception as e:
                text_location = "Местоположение не определено"
                logger.error('Failed to get text location in weather response: ' + str(e))
            bot_message = await message.reply_photo(caption=text_location, photo=open("weather.jpg", "rb"))
            await asyncio.sleep(600)
            await message.delete()
            await bot_message.delete()
    except Exception as e:
        logger.error('Failed to get weather: ' + str(e))
        bot_message = await message.reply(
            "Произошла ошибка при получении погоды",
            parse_mode=ParseMode.HTML,
        )
        await asyncio.sleep(3)
        await message.delete()
        await bot_message.delete()


async def switch(message: types.Message) -> None:
    try:
        member = await message.chat.get_member(message.from_user.id)
        username = message.from_user.mention
        logger.info(
            "New message: from chat: " + str(message.chat.title) + ", user_name: " + str(
                username) + ", message: " + str(message.text) + ", message_id: " + str(
                message.message_id) + ", user_id: " + str(
                message.from_user.id) + ", chat_id: " + str(
                message.chat.id) + ", status: " + str(member.status))
        if str(message.text).lower() == 'да':
            logger.info("Handle yes: " + str(username))
            await message.reply(
                "Пизда 😎",
                parse_mode=ParseMode.HTML,
            )
        if str(message.text).lower() == 'yes':
            logger.info("Handle yes: " + str(username))
            await message.reply(
                "Pizdes 😎",
                parse_mode=ParseMode.HTML,
            )
        if str(message.text).lower() == 'xdd' or str(message.text).lower() == 'хдд':
            if not message.from_user.is_bot:
                logger.info("xdd: " + str(username))
                await message.delete()
                await message.answer_sticker(
                    sticker='CAACAgIAAxkBAAEFlthi_NZPHFXutw4ZIr6mIJJrK1tDiwACXRoAApJdYEtMTTimqH0G8ykE')
        if str(message.text).lower() == 'pog' or str(message.text).lower() == 'пог':
            if not message.from_user.is_bot:
                logger.info("pog: " + str(username))
                await message.delete()
                await message.answer_sticker(
                    sticker='CAACAgIAAxkBAAEFmX5i_jcijaQtdlgGZDEknCwJSSg2VgACBgADezwGEd4e2v_l10SjKQQ')
        if str(message.text) == '/start@Crocodile_Covid_Bot':
            if not message.from_user.is_bot:
                logger.info("start Crocodile_Covid_Bot: " + str(username))
                await message.reply_sticker(
                    sticker='CAACAgIAAxkBAAEFmZdi_kfHvMkYVkaYF3U03XvpLnLrUAAC4h4AAsevYUua8eZ4oiN5hCkE')
        if 'genshin' in str(message.text).lower() or 'геншин' in str(message.text).lower():
            if not message.from_user.is_bot:
                logger.info("genshin: " + str(username))
                # await message.reply_sticker(
                #    sticker='CAACAgIAAxkBAAEFpB5jA2hRcSZ0Voo1LpQpuLDjw2vixAACDRcAAmRKKUnevtb6fKAwdSkE')
        if '300' in str(message.text).lower().split() or 'триста' in str(message.text).lower().split():
            if not message.from_user.is_bot:
                logger.info("300: " + str(username))
                await message.reply(text='Отсоси у тракториста 😊')
    except Exception as e:
        logger.error('New message: ' + str(e))


@dp.message_handler(commands=['revive', 'rv'])
async def revive(message: types.Message):
    logger.info("revive request")
    try:
        if await is_old_message(message):
            return
        await message.delete()
        username = message.from_user.mention
        logger.info(
            "Revive request: from: " + str(username) + ", chat_name: " + str(
                message.chat.title) + ", chat_id: " + str(
                message.chat.id))
        user_id = message.from_user.id
        member = await message.chat.get_member(user_id)
        logger.info("Revive: member status: " + member.status)
        if member.status == 'member' or member.status == 'left' or member.status == 'restricted' or member.status == 'kicked':
            try:
                until_date = (int(time.time()) + 1500)
                await message.chat.restrict(message.from_user.id,
                                            ChatPermissions(can_send_messages=False),
                                            until_date=until_date)
                await message.answer(
                    "💥 " + message.from_user.get_mention(
                        as_html=True) + " добровольно покинул(а) чат\nРеспаун через 25 минут." + random.choice(
                        sad_emoji), parse_mode=ParseMode.HTML)

            except Exception as e:
                logger.error('Failed revive kill: ' + str(e))
                bot_message = await message.answer(
                    message.from_user.get_mention(as_html=True) + ", админы неуязвимы 😭",
                    parse_mode=ParseMode.HTML)
                await asyncio.sleep(3)
                await bot_message.delete()
        else:
            bot_message = await message.answer(
                message.from_user.get_mention(as_html=True) + ", админы неуязвимы 😭",
                parse_mode=ParseMode.HTML)
            await asyncio.sleep(3)
            await bot_message.delete()
    except Exception as e:
        logger.error('Failed revive: ' + str(e))


@dp.message_handler(commands=['del'])
async def del_message(message: types.Message):
    logger.info("Delete message request")
    try:
        if await is_old_message(message):
            return
        await message.delete()
        if message.reply_to_message is not None:
            if message.from_user.id != 220117151:
                logger.info("Delete message: perm denied: " + str(message.from_user.id))
            else:
                logger.info("Delete message: try deleting message w text: " + str(message.reply_to_message.text))
                await bot.delete_message(chat_id=message.chat.id, message_id=message.reply_to_message.message_id)
        else:
            msg_id = message.get_args().strip()
            if not msg_id or len(msg_id) == 0:
                logger.info("Delete message: msg_id in message not found")
            else:
                if message.from_user.id != 220117151:
                    logger.info("Delete message: perm denied: " + str(message.from_user.id))
                else:
                    logger.info("Delete message: try deleting message w id: " + str(msg_id))
                    await bot.delete_message(chat_id=-1001173473651, message_id=int(msg_id))
    except Exception as e:
        logger.error('Failed to del msg: ' + str(e))


@dp.message_handler(commands=['ban'])
async def ban(message: types.Message):
    logger.info("ban request")
    try:
        if await is_old_message(message):
            return
        await message.delete()
        if message.reply_to_message is not None:
            if message.from_user.id != 220117151:
                logger.info("Ban: perm denied: " + str(message.from_user.id))
            else:
                logger.info("Ban: try ban user: " + str(message.reply_to_message.from_user.id))
                await bot.restrict_chat_member(chat_id=message.chat.id,
                                               user_id=int(message.reply_to_message.from_user.id),
                                               permissions=ChatPermissions(can_send_messages=False))
        else:
            logger.info("Ban: reply message not found")
    except Exception as e:
        logger.error('Failed to ban user: ' + str(e))


@dp.message_handler(commands=['addpoints'])
async def add_points(message: types.Message):
    logger.info("add points request")
    try:
        if await is_old_message(message):
            return
        await message.delete()
        if message.reply_to_message is not None:
            if message.from_user.id != 220117151:
                logger.info("Add points: perm denied: " + str(message.from_user.id))
            else:
                count_points = int(message.get_args().strip())
                logger.info("Add points: try add points user: " + str(
                    message.reply_to_message.from_user.id) + ", points' " + str(count_points))
                first_user_id = message.reply_to_message.from_user.id
                first_user_db = dbRoulette.search(UserQuery.id == first_user_id)
                first_user_points = 0
                if not first_user_db:
                    logger.info("Add points: new user")
                    dbRoulette.insert({'id': first_user_id, 'points': count_points, 'ts': int(time.time()) - 9000,
                                       'user_mention': message.reply_to_message.from_user.full_name})
                else:
                    first_user_points = first_user_db[0]['points']
                    logger.info("Add points: exists user, points:" + str(first_user_points))
                    first_user_points = int(first_user_points) + int(count_points)
                    logger.info("Add points: exists user, new points:" + str(first_user_points))
                    dbRoulette.update({'id': first_user_id, 'points': first_user_points},
                                      UserQuery.id == first_user_id)
        else:
            logger.info("Add points: reply message not found")
    except Exception as e:
        logger.error('Failed to add points user: ' + str(e))


@dp.message_handler(commands=['mute'])
async def mute(message: types.Message):
    logger.info("mute request")
    try:
        if await is_old_message(message):
            return
        await message.delete()
        if message.reply_to_message is not None:
            if message.from_user.id != 220117151:
                logger.info("Mute: perm denied: " + str(message.from_user.id))
            else:
                seconds = int(message.get_args().strip())
                logger.info("Mute: try mute user: " + str(message.reply_to_message.from_user.id) + " for " + str(
                    seconds) + " seconds")
                until_date = (int(time.time()) + seconds)
                await bot.restrict_chat_member(chat_id=message.chat.id,
                                               user_id=int(message.reply_to_message.from_user.id),
                                               permissions=ChatPermissions(can_send_messages=False),
                                               until_date=until_date)
        else:
            user_id = message.get_args().strip()
            if not user_id or len(user_id) == 0:
                logger.info("Mute: user_id in message not found")
            else:
                if message.from_user.id != 220117151:
                    logger.info("Mute: perm denied: " + str(message.from_user.id))
                else:
                    logger.info("Mute: try mute user: " + str(user_id))
                    until_date = (int(time.time()) + 3600)
                    await bot.restrict_chat_member(chat_id=-1001173473651, user_id=int(user_id),
                                                   permissions=ChatPermissions(can_send_messages=False),
                                                   until_date=until_date)
    except Exception as e:
        logger.error('Failed to mute user: ' + str(e))


@dp.message_handler(commands=['unmute', 'unban'])
async def unmute(message: types.Message):
    logger.info("unmute request")
    try:
        if await is_old_message(message):
            return
        await message.delete()
        if message.reply_to_message is not None:
            if message.from_user.id != 220117151:
                logger.info("Unmute: perm denied: " + str(message.from_user.id))
            else:
                logger.info("Unmute: try unmute user: " + str(message.reply_to_message.from_user.id))
                await bot.restrict_chat_member(chat_id=message.chat.id,
                                               user_id=int(message.reply_to_message.from_user.id),
                                               permissions=ChatPermissions(can_send_messages=False),
                                               until_date=(int(time.time()) + 60))
        else:
            user_id = message.get_args().strip()
            if not user_id or len(user_id) == 0:
                logger.info("Unmute: user_id in message not found")
            else:
                if message.from_user.id != 220117151:
                    logger.info("Unmute: perm denied: " + str(message.from_user.id))
                else:
                    logger.info("Unmute: try mute user: " + str(user_id))
                    await bot.restrict_chat_member(chat_id=-1001173473651, user_id=int(user_id),
                                                   permissions=ChatPermissions(can_send_messages=False),
                                                   until_date=(int(time.time()) + 60))
    except Exception as e:
        logger.error('Failed to unmute user: ' + str(e))


def numeral_noun_declension(
        number,
        nominative_singular,
        genetive_singular,
        nominative_plural
):
    return (
            (number in range(5, 20)) and nominative_plural or
            (1 in (number, (diglast := number % 10))) and nominative_singular or
            ({number, diglast} & {2, 3, 4}) and genetive_singular or nominative_plural
    )


@dp.message_handler(commands=['points', 'ps'])
async def points(message: types.Message):
    logger.info("points request")
    try:
        if await is_old_message(message):
            return
        await message.delete()
        user_id = message.from_user.id
        member = await message.chat.get_member(user_id)
        logger.info("points: member status: " + member.status)
        last_timestamp = dbRoulette.search(UserQuery.id == user_id)
        midas_points = 0
        if not last_timestamp:
            midas_points = 0
        else:
            midas_points = last_timestamp[0]['points']
            logger.info('points: points:'f"{midas_points=}")
        bot_message = await message.answer(
            "У " + message.from_user.get_mention(as_html=True) + " " + str(midas_points) + " " + str(
                numeral_noun_declension(midas_points, "очко", "очка", "очков")) + ".", parse_mode=ParseMode.HTML)
        await asyncio.sleep(10)
        await bot_message.delete()
    except Exception as e:
        logger.error('Failed points: ' + str(e))


@dp.message_handler(commands=['top10', 't'])
async def top10(message: types.Message):
    logger.info("top10 request")
    try:
        if await is_old_message(message):
            return
        await message.delete()
        username = message.from_user.mention
        logger.info(
            "Top10 request: from: " + str(username) + ", chat_name: " + str(
                message.chat.title) + ", chat_id: " + str(
                message.chat.id))
        logger.info("Top10 request")
        list = []
        lines = []
        if exists('roulette/dbRoulette.json'):
            file = open('roulette/dbRoulette.json', encoding='utf-8')
            jsonFile = None
            try:
                jsonFile = json.load(file)
            except:
                pass
            file.close()
            if jsonFile != None:
                jsonStrings = []
                for value in jsonFile["_default"]:
                    jsonStrings.append(jsonFile['_default'][value])
                lines = sorted(jsonStrings, key=lambda k: k['points'], reverse=True)
                index = 0
                for record in lines:
                    logger.info(str(index))
                    if index == 10:
                        break
                    logger.info("Top 10, element: " + str(record))
                    list.append(record['user_mention'] + " имеет " + str(record['points']) + str(
                        numeral_noun_declension(int(record['points']), " очко", " очка", " очков")))
                    index += 1
        if len(lines) == 0:
            bot_message = await message.answer(
                "Топ 10 по очкам 🔥:\n" + "Ещё ни у кого нет поинтов :(\nСтань первым :)! /roulette",
                parse_mode=ParseMode.HTML)
            await asyncio.sleep(3)
            await bot_message.delete()
        else:
            bot_message = await message.answer(
                "Топ 10 по очкам 🔥:\n" + "\n".join(str(e) for e in list))
            await asyncio.sleep(60)
            await bot_message.delete()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('Failed top10: ' + str(e) + ", line: " + str(exc_tb.tb_lineno))


@dp.message_handler(commands=['bottom10', 'b'])
async def bottom10(message: types.Message):
    logger.info("bottom10 request")
    try:
        if await is_old_message(message):
            return
        await message.delete()
        username = message.from_user.mention
        logger.info(
            "Bottom10 request: from: " + str(username) + ", chat_name: " + str(
                message.chat.title) + ", chat_id: " + str(
                message.chat.id))
        list = []
        lines = []
        if exists('roulette/dbRoulette.json'):
            file = open('roulette/dbRoulette.json', encoding='utf-8')
            jsonFile = None
            try:
                jsonFile = json.load(file)
            except:
                pass
            file.close()
            if jsonFile != None:
                jsonStrings = []
                for value in jsonFile["_default"]:
                    jsonStrings.append(jsonFile['_default'][value])
                lines = sorted(jsonStrings, key=lambda k: k['points'], reverse=False)
                index = 0
                for record in lines:
                    if index == 10:
                        break
                    logger.info("Bottom 10, element: " + str(record))
                    list.append(record['user_mention'] + " имеет " + str(record['points']) + str(
                        numeral_noun_declension(int(record['points']), " очко", " очка", " очков")))
                    index += 1
        if len(lines) == 0:
            bot_message = await message.answer(
                "😢 Меньше всего очков у:\n" + "Ещё ни у кого нет поинтов :(\nСтань первым :)! /roulette",
                parse_mode=ParseMode.HTML)
            await asyncio.sleep(3)
            await bot_message.delete()
        else:
            bot_message = await message.answer(
                "😢 Меньше всего очков у:\n" + "\n".join(str(e) for e in list))
            await asyncio.sleep(60)
            await bot_message.delete()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('Failed bottom10: ' + str(e) + ", line: " + str(exc_tb.tb_lineno))


@dp.message_handler(commands=['say'])
async def say(message: types.Message):
    logger.info("Say message request")
    try:
        if await is_old_message(message):
            return
        await message.delete()
        text = message.get_args().strip()
        if message.from_user.id != 220117151:
            logger.info("Say message: perm denied: " + str(message.from_user.id))
        else:
            if message.reply_to_message is None:
                logger.info("Say message: try say message w text: " + str(text))
                await bot.send_message(chat_id=message.chat.id, text=str(text))
            else:
                logger.info("Reply message: try repoly to message w text: " + str(
                    message.reply_to_message.text) + ", text: " + str(text))
                await bot.send_message(chat_id=message.chat.id, text=str(text),
                                       reply_to_message_id=message.reply_to_message.message_id)
    except Exception as e:
        logger.error('Failed to say message user: ' + str(e))


@dp.message_handler(commands=['sayc'])
async def say_to_cake(message: types.Message):
    logger.info("Say to cake message request")
    try:
        if await is_old_message(message):
            return
        await message.delete()
        text = message.get_args().strip()
        if message.from_user.id != 220117151:
            logger.info("Say to cake message: perm denied: " + str(message.from_user.id))
        else:
            if message.reply_to_message is None:
                logger.info("Say to cake message: try say message w text: " + str(text))
                await bot.send_message(chat_id=-1001173473651, text=str(text))
            else:
                logger.info("Reply to cake  message: try repoly to message w text: " + str(
                    message.reply_to_message.text) + ", text: " + str(text))
                await bot.send_message(chat_id=-1001173473651, text=str(text),
                                       reply_to_message_id=message.reply_to_message.message_id)
    except Exception as e:
        logger.error('Failed to say to cake message user: ' + str(e))


@dp.message_handler(commands=['checkpermissions'])
async def check_permissions(message: types.Message):
    logger.info("Check permissions request")
    try:
        if await is_old_message(message):
            return
        await message.delete()
        text = message.get_args().strip()
        if message.from_user.id != 220117151:
            logger.info("Check permissions: perm denied: " + str(message.from_user.id))
        else:
            logger.info("Check permissions: try check permissions...: ")
            member = await bot.get_chat_member(chat_id=-1001173473651, user_id=int(TOKEN.split(":")[0]))
            # member = await bot.get_chat_member(chat_id=message.chat.id, user_id=int(TOKEN.split(":")[0]))
            logger.info("Check permissions: member:" + str(member))
    except Exception as e:
        logger.error('Failed check permissions: ' + str(e))


@dp.message_handler(content_types=[types.ContentType.NEW_CHAT_MEMBERS])
async def on_new_chat_member(message: types.Message):
    for new_member in message.new_chat_members:
        if new_member.is_bot:
            continue
        new_member_username = new_member.mention
        logger.info("New user:" + str(new_member_username))
        logger.info("New user: " + str(new_member.username))
        bot_message = await message.reply(
            f"{new_member.get_mention(as_html=True)}, привет! Кого бы трахнул(а) из Вселенной Гарри Поттера? Фантастические твари считаются. 😳 P.S. Если ты новенький, то попытай счастья в рулетке /roulette :)",
            parse_mode=ParseMode.HTML,
        )
        await asyncio.sleep(60 * 60)
        await bot_message.delete()


@dp.message_handler(content_types=[types.ContentType.STICKER])
async def handle_sticker(message: types.Message):
    # logger.info("Sticker file id: " + message.sticker.file_unique_id)
    try:
        if message.sticker.file_unique_id == 'AgADXRoAApJdYEs':
            logger.info("Sticker: " + str(message.sticker.file_unique_id))
            await message.answer_sticker(
                sticker='CAACAgIAAxkBAAEFlthi_NZPHFXutw4ZIr6mIJJrK1tDiwACXRoAApJdYEtMTTimqH0G8ykE')
    except:
        pass
    try:
        if message.sticker.file_unique_id == 'AgADfxoAAjAf0Uk':
            logger.info("Sticker: " + str(message.sticker.file_unique_id))
            await message.answer_sticker(
                sticker='CAACAgIAAxkBAAEFmoJi_zgoHrylgXeUlrxUB94RiIwC2AACfxoAAjAf0UnKR8QKFENRVSkE')
    except:
        pass


duel_is_started = False
duel_first_user_message: types.Message
duel_second_user_message: types.Message
duel_roll_started = False
duel_wait_another_message: types.Message
duel_wait_another_sticker: types.Message
duel_points: int


@dp.message_handler(commands=['duel', 'd'])
async def duel(message: types.Message):
    logger.info("duel request")
    global duel_is_started, duel_points, duel_first_user_message, duel_second_user_message, duel_wait_another_message, \
        duel_roll_started, duel_wait_another_sticker
    try:
        if await is_old_message(message):
            return

        if duel_is_started:
            await message.delete()
            bot_m = await message.answer(
                message.from_user.get_mention(
                    as_html=True) + ", уже проходит активная дуэль",
                parse_mode=ParseMode.HTML)
            logger.info("Duel, send message: " + str(bot_m.text))
            await asyncio.sleep(5)
            await bot_m.delete()
            logger.info("Duel: another duel already started")
            return

        if not message.reply_to_message:
            bot_m = await message.answer(
                message.from_user.get_mention(
                    as_html=True) + ", Отправь <code>/duel 50</code>(количество банка) в ответ на сообщение тому, кому предлагаешь дуэль",
                parse_mode=ParseMode.HTML)
            logger.info("Duel, send message: " + str(bot_m.text))
            await message.delete()
            await asyncio.sleep(10)
            await bot_m.delete()
            return

        if message.reply_to_message.from_user.is_bot:
            bot_m = await message.answer(
                message.from_user.get_mention(as_html=True) + ", боты неуязвимы для дуэли 😎",
                parse_mode=ParseMode.HTML)
            logger.info("Duel, send message: " + str(bot_m.text))
            await message.delete()
            await asyncio.sleep(5)
            await bot_m.delete()
            return

        second_member = await message.chat.get_member(message.reply_to_message.from_user.id)
        first_member = await message.chat.get_member(message.from_user.id)
        logger.info("Duel, first member status: " + first_member.status)
        logger.info("Duel, second member status: " + second_member.status)
        check_first_member = False
        check_second_member = False
        if first_member.status == 'member' or first_member.status == 'left' or first_member.status == 'restricted' or first_member.status == 'kicked':
            check_first_member = True
        if second_member.status == 'member' or second_member.status == 'left' or second_member.status == 'restricted' or second_member.status == 'kicked':
            check_second_member = True

        if not check_first_member or not check_second_member:
            bot_m = await message.answer(
                message.from_user.get_mention(as_html=True) + ", ты или твой соперник неуязвим для дуэли 😭",
                parse_mode=ParseMode.HTML)
            logger.info("Duel, send message: " + str(bot_m.text))
            await message.delete()
            await asyncio.sleep(5)
            await bot_m.delete()
            return

        if message.from_user.id == message.reply_to_message.from_user.id:
            await message.delete()
            bot_m = await message.answer(
                message.from_user.get_mention(as_html=True) + ", Нельзя вызвать себя же на дуэль! 😡",
                parse_mode=ParseMode.HTML)
            logger.info("DuelAssign, send message: " + str(bot_m.text))
            await message.delete()
            await asyncio.sleep(5)
            await bot_m.delete()
            duel_second_user_message = None
            logger.info("DuelAssign: equals id")
            return

        points_bet = message.get_args().strip()
        if not points_bet or len(points_bet) == 0:
            bot_m = await message.answer(
                message.from_user.get_mention(
                    as_html=True) + ", ты не указал ставку для дуэли, пример <code>/duel 50</code>",
                parse_mode=ParseMode.HTML)
            logger.info("Duel, send message: " + str(bot_m.text))
            await message.delete()
            await asyncio.sleep(5)
            await bot_m.delete()
            logger.info("Duel: bet is none")
            return

        if int(points_bet) <= 0:
            bot_m = await message.answer(
                message.from_user.get_mention(as_html=True) + ", ставка = минимум 1",
                parse_mode=ParseMode.HTML)
            logger.info("Duel, send message: " + str(bot_m.text))
            await message.delete()
            await asyncio.sleep(5)
            await bot_m.delete()
            logger.info("Duel: bet is zero")
            return

        if int(points_bet) > 500:
            bot_m = await message.answer(
                message.from_user.get_mention(as_html=True) + ", ставка = максимум 500",
                parse_mode=ParseMode.HTML)
            logger.info("Duel, send message: " + str(bot_m.text))
            await message.delete()
            await asyncio.sleep(5)
            await bot_m.delete()
            logger.info("Duel: bet is max")
            return

        duel_is_started = True
        duel_points = int(points_bet)
        duel_first_user_message = message
        duel_second_user_message = message.reply_to_message
        await message.delete()
        duel_wait_another_message = await message.answer(
            "😱 " + duel_first_user_message.from_user.get_mention(
                as_html=True) + " вызвал на дуэль " + duel_second_user_message.from_user.get_mention(as_html=True)
            + "\nСтавка: " + str(duel_points) + str(
                numeral_noun_declension(int(duel_points), " очко", " очка", " очков"))
            + "\nВторой дуэлянт должен согласиться на дуэль командой /go (у него есть 3 минуты)"
            + "\nОба могут отменить дуэль командой /dc",
            parse_mode=ParseMode.HTML)
        duel_wait_another_sticker = await message.answer_sticker(
            sticker='CAACAgIAAxkBAAEFqCBjBUjK__Iq4NVApcij-UEqFJLnRgACXxwAAlp2MEh0574YlXmWjSkE')
        logger.info("Duel, send message: " + str(duel_wait_another_message.text))
        logger.info("Duel: wait another user")
        await asyncio.sleep(180)
        if not duel_is_started:
            logger.info('Duel: clean duel 1')
            duel_first_user_message = None
            duel_second_user_message = None
            duel_points = None
            duel_is_started = False
            duel_roll_started = False
            try:
                await duel_wait_another_message.delete()
            except:
                pass
            try:
                await duel_wait_another_sticker.delete()
            except:
                pass
    except Exception as e:
        logger.info('Duel: clean duel 2')
        duel_first_user_message = None
        duel_second_user_message = None
        duel_points = None
        duel_is_started = False
        duel_roll_started = False
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('Failed in duel: ' + str(e) + ", line: " + str(exc_tb.tb_lineno))


@dp.message_handler(commands=['dc'])
async def duel_cancel(message: types.Message):
    logger.info("duel cancel request")
    global duel_is_started, duel_points, duel_first_user_message, duel_second_user_message, duel_wait_another_message, \
        duel_roll_started, duel_wait_another_sticker

    try:
        if await is_old_message(message):
            return

        if duel_roll_started:
            await message.delete()
            bot_m = await message.answer(
                message.from_user.get_mention(
                    as_html=True) + ", дуэль уже началась, её нельзя отменить!",
                parse_mode=ParseMode.HTML)
            logger.info("Duel cancel, send message: " + str(bot_m.text))
            await asyncio.sleep(5)
            await bot_m.delete()
            logger.info("Duel cancel: duel and roll already started")
            return

        if duel_is_started:
            logger.info("cancel: duel_is_started")
        else:
            logger.info("cancel: duel_is_started not started")

        if duel_first_user_message is None:
            logger.info("cancel: duel_first_user_message = is None")
        else:
            logger.info("cancel: duel_first_user_message != is None")

        if duel_second_user_message is None:
            logger.info("cancel: duel_second_user_message = is None")
        else:
            logger.info("cancel: duel_second_user_message != is None")

        if duel_points is None:
            logger.info("cancel: duel_points = is None")
        else:
            logger.info("cancel: duel_points != is None")

        if not duel_is_started or duel_first_user_message is None or duel_second_user_message is None or duel_points is None:
            await message.delete()
            logger.info("DuelCancel: duel already finished")
            return

        await message.delete()

        if duel_second_user_message.from_user.id != message.from_user.id and duel_first_user_message.from_user.id != message.from_user.id:
            bot_m = await message.answer(
                message.from_user.get_mention(as_html=True) + ", Нельзя отменить чужую дуэль! 😡",
                parse_mode=ParseMode.HTML)
            logger.info("DuelCancel, send message: " + str(bot_m.text))
            await asyncio.sleep(5)
            await bot_m.delete()
            logger.info("DuelCancel: second user and duel assign not equals id")
            return

        logger.info('Duel cancel: canceling duel')
        duel_first_user_message = None
        duel_second_user_message = None
        duel_points = None
        duel_is_started = False
        duel_roll_started = False

        if duel_wait_another_message is not None:
            try:
                await duel_wait_another_message.delete()
            except:
                pass
        if duel_wait_another_sticker is not None:
            try:
                await duel_wait_another_sticker.delete()
            except:
                pass
    except Exception as e:
        logger.info('Duel cancel: clean duel error')
        duel_first_user_message = None
        duel_second_user_message = None
        duel_points = None
        duel_is_started = False
        duel_roll_started = False
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('Failed in duel cancel: ' + str(e) + ", line: " + str(exc_tb.tb_lineno))


@dp.message_handler(commands=['go'])
async def duel_assign(message: types.Message):
    logger.info("duel assign request")
    global duel_is_started, duel_points, duel_first_user_message, duel_second_user_message, duel_wait_another_message, \
        duel_roll_started, duel_wait_another_sticker

    try:
        if await is_old_message(message):
            return

        if duel_roll_started:
            await message.delete()
            bot_m = await message.answer(
                message.from_user.get_mention(
                    as_html=True) + ", уже проходит активная дуэль",
                parse_mode=ParseMode.HTML)
            logger.info("Duel, send message: " + str(bot_m.text))
            await asyncio.sleep(5)
            await bot_m.delete()
            logger.info("Duel: another duel already started")
            return

        if duel_is_started:
            logger.info("duel_is_started")
        else:
            logger.info("duel_is_started not started")

        if duel_first_user_message is None:
            logger.info("duel_first_user_message = is None")
        else:
            logger.info("duel_first_user_message != is None")

        if duel_second_user_message is None:
            logger.info("duel_second_user_message = is None")
        else:
            logger.info("duel_second_user_message != is None")

        if duel_points is None:
            logger.info("duel_points = is None")
        else:
            logger.info("duel_points != is None")

        if not duel_is_started or duel_first_user_message is None or duel_second_user_message is None or duel_points is None:
            await message.delete()
            bot_m = await message.answer(
                message.from_user.get_mention(
                    as_html=True) + ", дуэль закончилась",
                parse_mode=ParseMode.HTML)
            logger.info("DuelAssign, send message: " + str(bot_m.text))
            await asyncio.sleep(5)
            await bot_m.delete()
            logger.info('Duel: clean duel 3')
            duel_first_user_message = None
            duel_second_user_message = None
            duel_points = None
            duel_is_started = False
            duel_roll_started = False
            logger.info("DuelAssign: another duel already finished")
            return

        if duel_first_user_message.from_user.id == duel_second_user_message.from_user.id:
            await message.delete()
            bot_m = await message.answer(
                message.from_user.get_mention(as_html=True) + ", Нельзя согласиться на свою дуэль! 😡",
                parse_mode=ParseMode.HTML)
            logger.info("DuelAssign, send message: " + str(bot_m.text))
            await asyncio.sleep(5)
            await bot_m.delete()
            duel_second_user_message = None
            logger.info("DuelAssign: equals id")
            return

        await message.delete()

        if duel_second_user_message.from_user.id != message.from_user.id or duel_first_user_message.from_user.id == message.from_user.id:
            bot_m = await message.answer(
                message.from_user.get_mention(as_html=True) + ", Нельзя согласиться на чужую дуэль! 😡",
                parse_mode=ParseMode.HTML)
            logger.info("DuelAssign, send message: " + str(bot_m.text))
            await asyncio.sleep(5)
            await bot_m.delete()
            logger.info("DuelAssign: second user and duel assign not equals id")
            return

        duel_roll_started = True

        first_user_id = duel_first_user_message.from_user.id
        second_user_id = duel_second_user_message.from_user.id
        first_user_db = dbRoulette.search(UserQuery.id == first_user_id)
        second_user_db = dbRoulette.search(UserQuery.id == second_user_id)
        first_user_points = 0
        second_user_points = 0
        if not first_user_db:
            dbRoulette.insert({'id': first_user_id, 'points': 0, 'ts': int(time.time()) - 9000,
                               'user_mention': duel_first_user_message.from_user.full_name})
        else:
            first_user_points = first_user_db[0]['points']
            logger.info('duel: first user points:'f"{first_user_points=}")
        if not second_user_db:
            dbRoulette.insert({'id': second_user_id, 'points': 0, 'ts': int(time.time()) - 9000,
                               'user_mention': duel_second_user_message.from_user.full_name})
        else:
            second_user_points = second_user_db[0]['points']
            logger.info('duel: second user points:'f"{second_user_points=}")

        if first_user_points < duel_points:
            bot_m = await message.answer(
                "У " + duel_first_user_message.from_user.get_mention(
                    as_html=True) + " нет столько поинтов, у него всего "
                + str(first_user_points) + str(
                    numeral_noun_declension(int(first_user_points), " очко!", " очка!", " очков!")),
                parse_mode=ParseMode.HTML)
            logger.info("DuelAssign, send message: " + str(bot_m.text))
            logger.info("DuelAssign: first user points less bet")
            await asyncio.sleep(5)
            await bot_m.delete()
            logger.info('Duel: clean duel 4')
            duel_first_user_message = None
            duel_second_user_message = None
            duel_points = None
            duel_is_started = False
            duel_roll_started = False

        if second_user_points < duel_points:
            bot_m = await message.answer(
                "У " + duel_second_user_message.from_user.get_mention(
                    as_html=True) + " нет столько поинтов, у него всего "
                + str(second_user_points) + str(
                    numeral_noun_declension(int(second_user_points), " очко!", " очка!", " очков!")),
                parse_mode=ParseMode.HTML)
            logger.info("DuelAssign, send message: " + str(bot_m.text))
            logger.info("DuelAssign: second user points less bet")
            await asyncio.sleep(5)
            await bot_m.delete()
            logger.info('Duel: clean duel 5')
            duel_first_user_message = None
            duel_second_user_message = None
            duel_points = None
            duel_is_started = False
            duel_roll_started = False

        bot_start_duel_message = await message.answer(
            "🎲 Начинается дуэль между 🎲 " + duel_first_user_message.from_user.get_mention(as_html=True)
            + " и " + duel_second_user_message.from_user.get_mention(as_html=True)
            + " за " + str(duel_points) + str(numeral_noun_declension(int(duel_points), " очко!", " очка!", " очков!")),
            parse_mode=ParseMode.HTML)
        bot_first_user_rolls_duel_message = await message.answer(
            duel_first_user_message.from_user.get_mention(as_html=True) + " кидает 🎲...",
            parse_mode=ParseMode.HTML)
        rand_emoji = random.choice(['🎲', '🎳'])
        first_user_dice = await bot.send_dice(chat_id=message.chat.id, emoji=rand_emoji)
        logger.info("DuelAssign, first user dice is: " + str(first_user_dice.dice.value))
        first_user_dice_value = first_user_dice.dice.value

        bot_second_user_rolls_duel_message = await message.answer(
            duel_second_user_message.from_user.get_mention(as_html=True) + " кидает 🎲...",
            parse_mode=ParseMode.HTML)
        second_user_dice = await bot.send_dice(chat_id=message.chat.id, emoji=rand_emoji)
        logger.info("DuelAssign, second user dice is: " + str(second_user_dice.dice.value))
        second_user_dice_value = second_user_dice.dice.value
        bot_finish_duel_message = None
        await asyncio.sleep(10)
        if first_user_dice_value > second_user_dice_value:
            bot_finish_duel_message = await message.answer(
                "🎉 " + duel_first_user_message.from_user.get_mention(as_html=True)
                + "(выкинул " + str(
                    first_user_dice_value) + ") обыграл " + duel_second_user_message.from_user.get_mention(as_html=True)
                + "(выкинул " + str(second_user_dice_value) + ") и получает "
                + str(duel_points) + str(numeral_noun_declension(int(duel_points), " очко!", " очка!", " очков!"))
                + " 👏😎", parse_mode=ParseMode.HTML)
            first_user_points = int(first_user_points) + int(duel_points)
            dbRoulette.update({'id': first_user_id, 'points': first_user_points},
                              UserQuery.id == first_user_id)
            logger.info("duel: add first user points: " + str(first_user_points))
            second_user_points = int(second_user_points) - int(duel_points)
            dbRoulette.update({'id': second_user_id, 'points': second_user_points},
                              UserQuery.id == second_user_id)
            logger.info("duel: remove second user points: " + str(second_user_points))

        if first_user_dice_value < second_user_dice_value:
            bot_finish_duel_message = await message.answer(
                "🎉 " + duel_second_user_message.from_user.get_mention(as_html=True)
                + "(выкинул " + str(
                    second_user_dice_value) + ") обыграл " + duel_first_user_message.from_user.get_mention(as_html=True)
                + "(выкинул " + str(first_user_dice_value) + ") и получает "
                + str(duel_points) + str(numeral_noun_declension(int(duel_points), " очко!", " очка!", " очков!"))
                + " 👏😎", parse_mode=ParseMode.HTML)
            second_user_points = int(second_user_points) + int(duel_points)
            dbRoulette.update({'id': second_user_id, 'points': second_user_points},
                              UserQuery.id == second_user_id)
            logger.info("duel: add second user points: " + str(second_user_points))
            first_user_points = int(first_user_points) - int(duel_points)
            dbRoulette.update({'id': first_user_id, 'points': first_user_points},
                              UserQuery.id == first_user_id)
            logger.info("duel: remove first user points: " + str(first_user_points))

        if first_user_dice_value == second_user_dice_value:
            duel_points = (int(duel_points) * 2)
            bot_finish_duel_message = await message.answer(
                "😱 Ого! Оба выкинули одинаковую сторону! "
                + duel_second_user_message.from_user.get_mention(as_html=True)
                + "(выкинул " + str(second_user_dice_value) + ") и " + duel_first_user_message.from_user.get_mention(
                    as_html=True)
                + "(выкинул " + str(first_user_dice_value) + ")! Оба получают удвоенное количество очков: "
                + str(duel_points) + str(numeral_noun_declension(int(duel_points), " очко!", " очка!", " очков!"))
                + " 👏😎", parse_mode=ParseMode.HTML)
            first_user_points = int(first_user_points) + int(duel_points)
            dbRoulette.update({'id': first_user_id, 'points': first_user_points},
                              UserQuery.id == first_user_id)
            second_user_points = int(second_user_points) + int(duel_points)
            dbRoulette.update({'id': second_user_id, 'points': second_user_points},
                              UserQuery.id == second_user_id)
            logger.info("duel: add first user points: " + str(first_user_points)
                        + "and add second user points: " + str(second_user_points))

        await asyncio.sleep(30)

        logger.info('Duel: clean duel 6')
        duel_first_user_message = None
        duel_second_user_message = None
        duel_points = None
        duel_is_started = False
        duel_roll_started = False

        if bot_start_duel_message is not None:
            try:
                await bot_start_duel_message.delete()
            except:
                pass
        if duel_wait_another_message is not None:
            try:
                await duel_wait_another_message.delete()
            except:
                pass
        if duel_wait_another_sticker is not None:
            try:
                await duel_wait_another_sticker.delete()
            except:
                pass
        if bot_first_user_rolls_duel_message is not None:
            try:
                await bot_first_user_rolls_duel_message.delete()
            except:
                pass
        if bot_second_user_rolls_duel_message is not None:
            try:
                await bot_second_user_rolls_duel_message.delete()
            except:
                pass
        if first_user_dice is not None:
            try:
                await first_user_dice.delete()
            except:
                pass
        if second_user_dice is not None:
            try:
                await second_user_dice.delete()
            except:
                pass
        if bot_finish_duel_message is not None:
            try:
                await bot_finish_duel_message.delete()
            except:
                pass
    except Exception as e:
        logger.info('Duel: clean duel 7')
        duel_first_user_message = None
        duel_second_user_message = None
        duel_points = None
        duel_is_started = False
        duel_roll_started = False
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('Failed in duel assign: ' + str(e) + ", line: " + str(exc_tb.tb_lineno))


def main():
    dp.register_message_handler(switch)
    executor.start_polling(dp, skip_updates=False)


def get_pog_quote(mention: str) -> str:
    pog_quotes = [
        mention + " не выжил(а) после выстрела. Но пришла Женская версия Рофлана и реснула.",
        mention + " записан(а) в тетрадь смерти. Но пока карандашиком",
        mention + ", было близко, но пронесло",
        mention + " выиграл(а) в жмурки",
        mention + " глотнул(а) пивка неуязвимости",
        mention + " ХИЛИТСЯ-ЖИВЁТ!",
        mention + ": да кто этот ваш рулетка нахуй",
        mention + " а ты боялась - даже юбка не помялась",
        mention + " аегис релизовал(а) грамотно...",
        mention + " родился в рубашке",
        mention + " в последний момент роняет револьвер",
        mention + " стреляет холостыми",
    ]
    return random.choice(pog_quotes)


def get_dead_quote(mention: str):
    dead_quotes = [
        mention + " выжил(а) после выстрела, но пришла Сотоша и добила",
        mention + " душил(а) питона, но задушил(а) себя",
        mention + " почти выжил(а), но нет",
        mention + " выключили свет",
        mention + " заперт(а) в домике соития",
        mention + " корону пережил(а), а рулетку - нет",
        "МАМА, " + mention + " ФУРА УБИЛА",
        mention + " был задушен Киром. Кто-нибудь, откройте окно",
        mention + " даже в рулетке проиграл(а)",
        mention + " передознулся кринжатиной",
        mention + " жил до конца, умер как герой",
        mention + " не повезло, не повезло",
        mention + " уехал(а) жить в Лондон",
        mention + ", это были не те грибы...",
        mention + " заставили идти делать уроки",
    ]
    return random.choice(dead_quotes)


if __name__ == '__main__':
    main()
