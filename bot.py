import asyncio
import calendar
import logging
import os
import io
import random
import time
import json
import sys
import re
from datetime import datetime
from random import randrange
from uuid import uuid4
import requests
from dotenv import load_dotenv
from tinydb import TinyDB, Query
import subprocess
from sys import platform
from lxml import etree
from os.path import exists
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineQuery, InputTextMessageContent, InlineQueryResultArticle, InlineKeyboardMarkup, \
    InlineKeyboardButton, ParseMode, ChatPermissions
from pathlib import Path
from python_aternos import Client
from stt import STT
from summary import Summary
import openai
from asgiref.sync import sync_to_async
#from pyChatGPT import ChatGPT
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import pyimgur
from PIL import Image
import functools
import degenerator
import horoscope
import weather
import anime as anime_qq

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
ATERNOS_LOGIN = os.getenv("ATERNOS_LOGIN")
ATERNOS_PASSWORD = os.getenv("ATERNOS_PASSWORD")
ATERNOS_SENTRY_NAME = os.getenv("ATERNOS_SENTRY_NAME")
CHAT_GPT_ACCESS_IDS = os.getenv("CHAT_GPT_ACCESS_IDS")
DALL_E_ACCESS_IDS = os.getenv("DALL_E_ACCESS_IDS")
CAKE_CHAT_ID = os.getenv("CAKE_CHAT_ID")
CAKE_CHANNEL_ID = os.getenv("CAKE_CHANNEL_ID")
OWNER_USER_ID = os.getenv("OWNER_USER_ID")
ADMIN_USER_IDS = os.getenv("ADMIN_USER_IDS")
ATERNOS_ACCESS_IDS = os.getenv("ATERNOS_ACCESS_IDS")
STT_ACCESS_IDS = os.getenv("STT_ACCESS_IDS")
VOLJ_CHILL_CHANNEL_ID = os.getenv("VOLJ_CHILL_CHANNEL_ID")
VOLJ_CHILL_CHAT_ID = os.getenv("VOLJ_CHILL_CHAT_ID")
BOT_TEST_ROOM_CHAT_ID = os.getenv("BOT_TEST_ROOM_CHAT_ID")
IMGUR_ID = os.getenv("IMGUR_ID")
IMGFLIP_USERNAME = os.getenv("IMGFLIP_USERNAME")
IMGFLIP_PASSWORD = os.getenv("IMGFLIP_PASSWORD")

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
aternos = None
stt = STT()
summary_chat = Summary()
openai.api_key = os.getenv("OPENAI_API_KEY")


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


def get_hw_info():
    if platform == "linux":
        try:
            neofetch = subprocess.run(['neofetch','--stdout', '--color_blocks off', '--off'], capture_output=True,
                                        text=True).stdout.strip("\n")
            return neofetch
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
           '/roulette, /r - Русская рулетка: выживи или получи мут на 25 минут, шанс: количество пуль к 6(при выигрыше +(3 * на количество пуль)(по умолчанию одна пуля, количество пуль можно указать после команды(от 1 до 5 пуль)), при проигрыше -количество пуль в очках) КД 1 час\n' \
           '/duel, /d -  Отправить в ответ на сообщение того, кого хочешь вызвать на дуэль с указанием ставки. Очки проигравшего перейдут к выигрывшему\n' \
           '/midas, /m - Отправить в ответ на сообщение того, кого хочешь замидасить(рулетка на мут на 25 минут, шанс 1 к 3). Стоимость 30 очков\n' \
           '/revive, /rv - Добровольный мут на 25 минут\n' \
           '/points, /ps - Показать количество очков\n' \
           '/top10, /t - Показать топ 10 по очкам\n' \
           '/bottom10, /b - Показать у кого меньше всех очков\n' \
           '/coin, /c - Подбросить монетку\n' \
           '/anekdot /an - Случайный анекдот с anekdot.ru\n' \
           '/meme - Случайный фон под текст, просто рандом\n' \
           '/dmt - Создать демотиватор(укажите текст после команды или оставьте пустым для случайного)\n' \
           '/ask - Задать вопрос нейросети OpenAI GPT3 (c_a_k_e, nastjadd and voljchill chats only)\n' \
           '/image - Картинка по описанию от нейросети OpenAI DALL_E (voljchill chat only)\n' \
           '/horoscope - Гороскоп (/h)\n' \
           '/weather, /w - Узнать погоду, укажите город после команды'


def get_info_text():
    return 'Бот поддерживает как инлайн режим\n' \
           'Так и команды(для работы команд добавьте бота в группу и назначьте администратором)\n' \
           '/ping, /p - Погладить бота\n' \
           '/roulette, /r - Русская рулетка: выживи или получи мут на 25 минут, шанс: количество пуль к 6(при выигрыше +(3 очка * на количество пуль)(по умолчанию одна пуля, количество пуль можно указать после команды(от 1 до 5 пуль)), при проигрыше -количество пуль в очках) КД 1 час\n' \
           '/duel, /d -  Отправить в ответ на сообщение того, кого хочешь вызвать на дуэль с указанием ставки. Очки проигравшего перейдут к выигрывшему\n' \
           '/midas, /m - Отправить в ответ на сообщение того, кого хочешь замидасить(рулетка на мут на 25 минут, шанс 1 к 3). Стоимость 30 очков\n' \
           '/revive, /rv - Добровольный мут на 25 минут\n' \
           '/points, /ps - Показать количество очков\n' \
           '/top10, /t - Показать топ 10 по очкам\n' \
           '/bottom10, /b - Показать у кого меньше всех очков\n' \
           '/coin, /c - Подбросить монетку\n' \
           '/anekdot /an - Случайный анекдот с anekdot.ru\n' \
           '/meme - Случайный фон под текст, просто рандом\n' \
           '/dmt - Создать демотиватор(укажите текст после команды или оставьте пустым для случайного)\n' \
           '/ask - Задать вопрос нейросети OpenAI GPT3 (c_a_k_e, nastjadd and voljchill chats only)\n' \
           '/image - Картинка по описанию от нейросети OpenAI DALL_E (voljchill chat only)\n' \
           '/weather, /w - Узнать погоду, укажите город после команды\n' \
           '/horoscope - Гороскоп (/h)'


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    key_board = [
        [InlineKeyboardButton('НАЧАТЬ', switch_inline_query_current_chat='')],
    ]

    try:
        bot_message = await message.reply(get_start_text(),
                                          reply_markup=InlineKeyboardMarkup(inline_keyboard=key_board))
        #await asyncio.sleep(20)
        #await bot_message.delete()
        #await message.delete()
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


key_horoscope_result = [
    [
        InlineKeyboardButton('Овен', callback_data='Овен'),
        InlineKeyboardButton('Телец', callback_data='Телец'),
        InlineKeyboardButton('Близнецы', callback_data='Близнецы'),
        InlineKeyboardButton('Рак', callback_data='Рак'),
    ],
    [
        InlineKeyboardButton('Лев', callback_data='Лев'),
        InlineKeyboardButton('Дева', callback_data='Дева'),
        InlineKeyboardButton('Весы', callback_data='Весы'),
        InlineKeyboardButton('Скорпион', callback_data='Скорпион'),
     ],
    [
        InlineKeyboardButton('Стрелец', callback_data='Стрелец'),
        InlineKeyboardButton('Козерог', callback_data='Козерог'),
        InlineKeyboardButton('Водолей', callback_data='Водолей'),
        InlineKeyboardButton('Рыбы', callback_data='Рыбы'),
    ],
]


@dp.message_handler(commands=['horoscope', 'h'])
async def get_horoscope(message: types.Message):
    logger.info("horoscope request")
    try:
        if await is_old_message(message):
            return
        await message.reply(
                "Гороскоп: выберите знак",
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=key_horoscope_result)
            )
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('Failed horoscope: ' + str(e) + ", line: " + str(exc_tb.tb_lineno))


@dp.callback_query_handler()
async def callback_worker(call):
    try:
        print(call)
        horo = horoscope.getHoro(horoscope.request(), horoscope.apiSigns.get(call.data))
        await bot.send_message(chat_id=call.message.chat.id, text=call.from_user.get_mention(as_html=True) + ', гороскоп для ' + call.data + str(horo), parse_mode=ParseMode.HTML)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('Failed horoscope callback_worker: ' + str(e) + ", line: " + str(exc_tb.tb_lineno))
        await bot.send_message(chat_id=call.message.chat.id, text='Произошла ошибка при запросе гороскопа, попробуйте позднее')


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
            id=get_inline_id('anekdot'),
            title="Случайный анекдот",
            thumb_url='https://i.imgur.com/TonbezY.jpeg',
            input_message_content=InputTextMessageContent(get_random_anekdot_ru(),
                                                          parse_mode=ParseMode.HTML, disable_web_page_preview=True),
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
            id=get_inline_id('get_random_choiсe'),
            title="Орёл или решка",
            thumb_url='https://cdn.7tv.app/emote/61d1feb2752f555bcde94488/4x.png',
            input_message_content=InputTextMessageContent(get_random_choice(),
                                                          parse_mode=ParseMode.HTML),
        ),
        InlineQueryResultArticle(
            id=get_inline_id('get_sp'),
            title="Стикер-паки",
            thumb_url='https://i.imgur.com/QMIJ0aG.png',
            input_message_content=InputTextMessageContent(get_sp(),
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


def get_random_anekdot_ru():
    logger.info("anekdot request")
    try:
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.109 Safari/537.36 OPR/84.0.4316.52'
        }
        import requests
        from bs4 import BeautifulSoup
        url = 'https://www.anekdot.ru/random/anekdot/'
        page = requests.get(url, timeout=2)
        soup = BeautifulSoup(page.text, "html.parser")
        anekdot = soup.find(class_='text')
        anekdot = str(anekdot)
        anekdot = anekdot.replace('<div class="text">', '')
        anekdot = anekdot.replace('<br/>', '\n')
        anekdot = anekdot.replace('</div>', '')
        return anekdot
    except Exception as e:
        logger.error('Failed anekdot: ' + str(e))
        return 'Анекдот: Попробуйте позднее'


def get_random_choice():
    ret_text = ''
    edge = random.randint(1,100)
    if edge <=5:
        return 'Ребро!'
    side = random.randint(1,2)
    if side == 1:
        ret_text='Орёл'
    else:
        ret_text='Решка'
    return ret_text



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


def get_sp():
    try:
        return 'Стикер-паки от бота:\n' \
               'Кекисы:\n' \
               '1 https://t.me/addstickers/f_z1s2gryf_220117151_by_fStikBot\n' \
               '2 https://t.me/addstickers/Kekisy2\n' \
               '3 https://t.me/addstickers/Kekisy3\n' \
               '4 https://t.me/addstickers/kekisy4\n' \
               '5 https://t.me/addstickers/kekisy5\n' \
               'C_A_K_E https://t.me/addstickers/C_a_k_e_stickers\n' \
               'Emoji кекисы:\n' \
               '1 https://t.me/addemoji/kekisy1\n' \
               '2 https://t.me/addemoji/kekisy2emoji\n' \
               '3 https://t.me/addemoji/kekisy3emoji'
    except Exception as e:
        logger.error('Failed to get_sp: ' + str(e))
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
        #await message.delete()
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
        #await asyncio.sleep(20)
        #await bot_message.delete()
        #await message.delete()
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


@dp.message_handler(commands=['hwinfo', 'hw'])
async def stats(message: types.Message):
    logger.info("stats request")
    try:
        if await is_old_message(message):
            return
        bot_message = await message.reply_photo(photo="https://i.imgur.com/xVRpb8E.png", caption=get_hw_info())
    except Exception as e:
        logger.error('Failed stats: ' + str(e))


@dp.message_handler(commands=['coin', 'c'])
async def ping(message: types.Message):
    logger.info("coin request")
    try:
        if await is_old_message(message):
            return
        await message.delete()
        await message.answer(message.from_user.get_mention(as_html=True) + ' подбросил монетку: '+ get_random_choice(), parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error('Failed coin: ' + str(e))


@dp.message_handler(commands=['anekdot', 'an'])
async def ping(message: types.Message):
    logger.info("anekdot request")
    try:
        if await is_old_message(message):
            return
        await message.delete()
        await message.answer('Случайный /anekdot:\n'+ get_random_anekdot_ru(), parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error('Failed anekdot: ' + str(e))


def get_user_link_text(user_id, user_name):
    text = '<a href="tg://user?id=%s' % user_id + '">@%s' % user_name + '</a>'
    logger.info('get_user_link_text: 'f"{text=}")
    return text


def is_nan(num):
    return num != num


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
                message.from_user.get_mention(as_html=True) + ", не выбрано сообщение того, кого будем мидасить",
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


@dp.message_handler(commands=['summary', 'sum'])
async def summary(message: types.Message):
    logger.info("summary request")
    try:
        if await is_old_message(message):
            return
        await message.delete()
        analyze_message = await message.answer('Анализирую чат...', parse_mode=ParseMode.HTML)
        file_name = str(message.chat.id)
        summary_text = await sync_to_async(summary_chat.summary_text)(file_name)
        await analyze_message.delete()
        logger.info('Summary result:' + str(summary_text))
        await message.answer('Анализ чата на основе последних 25 сообщений: ' + str(summary_text), parse_mode=ParseMode.HTML)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('Failed summary: ' + str(e) + ", line: " + str(exc_tb.tb_lineno))


@dp.message_handler(commands=['meme'])
async def ask(message: types.Message):
    logger.info("meme request")
    try:
        if await is_old_message(message):
            return
        args = message.get_args().strip()
        if not args or len(args) == 0:
            bot_message = await message.reply(
                "Укажите одно или два слова через пробел",
                parse_mode=ParseMode.HTML,
            )
            await asyncio.sleep(3)
            await message.delete()
            await bot.delete_message(chat_id=bot_message.chat.id, message_id=bot_message.message_id)
        else:
            logger.info('meme, question: ' + args)
            username = IMGFLIP_USERNAME
            password = IMGFLIP_PASSWORD
            damn_data = requests.get('https://api.imgflip.com/get_memes').json()['data']['memes']
            memepics = [{'name': image['name'], 'url': image['url'], 'id': image['id']} for image in damn_data]
            test = args.split(' ')
            if len(test) > 2 or len(test) < 1:
                bot_message = await message.reply(
                    "Укажите одно или два слова через пробел",
                    parse_mode=ParseMode.HTML,
                )
                await asyncio.sleep(3)
                await message.delete()
                await bot.delete_message(chat_id=bot_message.chat.id, message_id=bot_message.message_id)
            txt1 = test[0]
            txt2 = None
            if len(test) == 2:
                txt2 = test[1]

            URL = 'https://api.imgflip.com/caption_image'
            params = {
                'username': username,
                'password': password,
                'template_id': memepics[random.randint(1, 100)]['id'],
                'text0': txt1,
                'text1': txt2
            }
            response = requests.request('POST', URL, params=params).json()
            logger.info('meme, response:' + response['data']['url'])
            await message.reply_photo(photo=response['data']['url'],
                                parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error('Failed to meme: ' + str(e))


@dp.message_handler(commands=['ask'])
async def ask(message: types.Message):
    logger.info("ask request")
    sticker = None
    try:
        if await is_old_message(message):
            return
        if str(message.chat.id) not in CHAT_GPT_ACCESS_IDS:
            return
        city = message.get_args().strip()
        if not city or len(city) == 0:
            bot_message = await message.reply(
                "Укажите вопрос после команды",
                parse_mode=ParseMode.HTML,
            )
            await asyncio.sleep(3)
            await message.delete()
            await bot.delete_message(chat_id=bot_message.chat.id, message_id=bot_message.message_id)
        else:
            logger.info('ask, question: ' + city)
            prmt = "Q: {qst}\nA:".format(qst=city)
            sticker = await message.reply_sticker(
                    sticker=get_search_sticker())
            response = await sync_to_async(openai.Completion.create)(model="text-davinci-003",
                                                                     prompt=prmt,
                                                                     temperature=1.0,
                                                                     max_tokens=2048,
                                                                     top_p=0.8,
                                                                     frequency_penalty=0.0,
                                                                     presence_penalty=0.0)
            logger.info('ask, response:' + response.choices[0].text)
            await sticker.delete()
            sticker = None
            bot_message = await message.reply('Ответ от OpenAI GPT3: ```\n' + response.choices[0].text.replace('```','') + '\n```', parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        logger.error('Failed to ask: ' + str(e))
        bot_message = await message.reply(
            "Произошла ошибка при обращении к OpenAI GPT3: " + str(e),
            parse_mode=ParseMode.HTML,
        )
        if sticker:
            await sticker.delete()


#@dp.message_handler(commands=['chat'])
async def chatgpt(message: types.Message):
    logger.info("chatgpt request")
    sticker = None
    try:
        if await is_old_message(message):
            return
        if str(message.chat.id) not in DALL_E_ACCESS_IDS:
            return
        question = message.get_args().strip()
        if not question or len(question) == 0:
            bot_message = await message.reply(
                "Укажите вопрос после команды",
                parse_mode=ParseMode.HTML,
            )
            await asyncio.sleep(3)
            await message.delete()
            await bot.delete_message(chat_id=bot_message.chat.id, message_id=bot_message.message_id)
        else:
            logger.info('chatgpt, question: ' + question)
            sticker = await message.reply_sticker(
                    sticker=get_search_sticker())
            resp = await sync_to_async(chatgpt_api.send_message)(question)
            logger.info('chatgpt, response:' + resp['message'])
            await sticker.delete()
            sticker = None
            bot_message = await message.reply('Ответ от OpenAI ChatGPT: ```\n' + resp['message'].replace('```','') + '\n```', parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        logger.error('Failed to chatgpt: ' + str(e))
        try:
            bot_message = await message.reply(
                "Произошла ошибка при обращении к OpenAI ChatGPT: " + str(e),
                parse_mode=ParseMode.HTML,
            )
        except:
             bot_message = await message.reply(
                "Произошла ошибка при обращении к OpenAI ChatGPT: Unknown Exception",
                parse_mode=ParseMode.HTML,
            )
        if sticker:
            await sticker.delete()


@dp.message_handler(commands=['image'])
async def dalle(message: types.Message):
    logger.info("DALL-E image request")
    try:
        if await is_old_message(message):
            return
        if str(message.chat.id) not in DALL_E_ACCESS_IDS:
            bot_message = await message.reply(
                "У вас нет прав для этой команды",
                parse_mode=ParseMode.HTML,
            )
            return
        description = message.get_args().strip()
        if not description or len(description) == 0:
            bot_message = await message.reply(
                "Укажите описание после команды",
                parse_mode=ParseMode.HTML,
            )
            await asyncio.sleep(3)
            await message.delete()
            await bot.delete_message(chat_id=bot_message.chat.id, message_id=bot_message.message_id)
        else:
            logger.info('DALL-E image, question: ' + description)
            prmt = "Q: {qst}\nA:".format(qst=description)
            response = await sync_to_async(openai.Image.create)(
                prompt=prmt,
                n=1,
                size="512x512"
            )
            logger.info('DALL-E image, response:' + response['data'][0]['url'])
            await message.reply('Ответ от DALL-E: <a href="{}">&#8204;</a>'.format(response['data'][0]['url']),
                                parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error('Failed to DALL-E: ' + str(e))
        bot_message = await message.reply(
            "Произошла ошибка при обращении к DALL-E: " + str(e),
            parse_mode=ParseMode.HTML,
        )
        #await asyncio.sleep(10)
        #await message.delete()
        #await bot_message.delete()


async def switch(message: types.Message) -> None:
    try:
        member = await message.chat.get_member(message.from_user.id)
        username = message.from_user.mention
        file_object = open('messages/chat_' + str(message.chat.id), 'a+', encoding='utf-8')
        user_name = ''
        if message.from_user.username:
            user_name = message.from_user.username
        if message.from_user.first_name:
            user_name = message.from_user.first_name
        file_object.write(user_name + ' пишет: ' + str(message.text) + '\n')
        #file_object.write(str(message.text) + '\n')
        file_object.close()
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
        if str(message.text).lower() == 'да пизда':
            logger.info("Handle yes2: " + str(username))
            await message.reply_sticker(
                sticker='CAACAgIAAxkBAAEGSN1jYhmlV7iTNoNv1Nuv35-9ksnfqwADIQAC_K8AAUibdSfeqI_efioE')
        if str(message.text).lower() == 'yes':
            logger.info("Handle yes: " + str(username))
            await message.reply(
                "Pizdes 😎",
                parse_mode=ParseMode.HTML,
            )
        if find_whole_word('увы')(str(message.text)):
            if not message.from_user.is_bot:
                logger.info("увы: " + str(username))
                await message.answer_sticker(
                    sticker='CAACAgIAAxkBAAEG2fJjnFnjPKRJD4836gUGOovzIGDRUAACqyIAAhfmkEhTcU-1XtA3hSwE')
        if find_whole_word('kappa')(str(message.text)) or find_whole_word('каппа')(str(message.text)):
            if not message.from_user.is_bot:
                logger.info("каппа: " + str(username))
                await message.answer_sticker(
                    sticker='CAACAgIAAxkBAAEHTUJjxmbRMC5uMJrPaPqGpEdx_LJoMgACDgMAAuB5UgcTQTG4A1bbVy0E')
        if find_whole_word('уы')(str(message.text)):
            if not message.from_user.is_bot:
                logger.info("уы: " + str(username))
                await message.answer_sticker(
                    sticker='CAACAgIAAxkBAAEHSQdjxYpNE1uIkfj-qyXEHmsKhwle_gACcSoAAkwSIUrCQBlAfjIt3i0E')
        if find_whole_word('1984')(str(message.text)):
            if not message.from_user.is_bot:
                logger.info("1984: " + str(username))
                await message.answer_sticker(
                    sticker='CAACAgIAAxkBAAEHXIRjypszy6aYzlnc2N_fqskTMAABjpAAAkgmAAJQLlhKiA2tO_8HjJgtBA')
        if find_whole_word('изи')(str(message.text)) or find_whole_word('ez')(str(message.text)) or find_whole_word('ezy')(str(message.text)):
            if not message.from_user.is_bot:
                logger.info("ez: " + str(username))
                await message.answer_sticker(
                    sticker='CAACAgIAAxkBAAEHKexjuaZv0tviCBQRzYNaI48fkJopjwACNwQAAug89xr6qohIKZJqPi0E')
        if find_whole_word('юля')(str(message.text)) or find_whole_word('шизя')(str(message.text)) or find_whole_word('юзя')(str(message.text)):
            if not message.from_user.is_bot:
                logger.info("uzy: " + str(username))
                await message.answer_sticker(
                    sticker='CAACAgIAAxkBAAEHXHtjyppGSRNkb_cCJNSqaAYIiBCtTQACYRoAAotm-Uhrqn-XuhrxXi0E')
        if find_whole_word('xdd')(str(message.text)) or find_whole_word('хдд')(str(message.text)):
            if not message.from_user.is_bot:
                logger.info("xdd: " + str(username))
                await message.answer_sticker(
                    sticker='CAACAgIAAxkBAAEHVTtjyLg59Kw7KlrSSqsSpW2nw3HKqAACgCMAAqzQ4EvYN2WqonJz_y0E')
        if find_whole_word('срать')(str(message.text)) or find_whole_word('насрано')(str(message.text)):
            if not message.from_user.is_bot:
                logger.info("srat: " + str(username))
                await message.answer_sticker(
                    sticker='CAACAgIAAxkBAAEHWmRjyltoDcmn6nNqslVvUrae3f7BmQACuCIAAvNvUUhdtnR8pPKdhy0E')
        if find_whole_word('сэдкот')(str(message.text)) or \
                find_whole_word('сэдкэт')(str(message.text)) or \
                find_whole_word('sadcat')(str(message.text)) or \
                find_whole_word('сэдкет')(str(message.text)):
            if not message.from_user.is_bot:
                logger.info("sadcat: " + str(username))
                await message.answer_sticker(
                    sticker='CAACAgIAAxkBAAEF3hVjJkoQVbtOAAGcqV864S0BwJIZxmkAAxwAAgxZCUn3jc34CkwKXikE')
        if find_whole_word('кекв')(str(message.text)) or find_whole_word('kekw')(str(message.text)):
            if not message.from_user.is_bot:
                logger.info("kekw: " + str(username))
                await message.answer_sticker(
                    sticker='CAACAgIAAxkBAAEGDBNjQzV8y_M8IpJBwPocAcTz84cCeAAC3QMAAuB5UgdGIcN1K0HvwSoE')
        if find_whole_word('pog')(str(message.text)) or find_whole_word('пог')(str(message.text)):
            if not message.from_user.is_bot:
                logger.info("pog: " + str(username))
                await message.answer_sticker(
                    sticker='CAACAgIAAxkBAAEFmX5i_jcijaQtdlgGZDEknCwJSSg2VgACBgADezwGEd4e2v_l10SjKQQ')
        if find_whole_word('пон')(str(message.text)) or find_whole_word('pon')(str(message.text)):
            if not message.from_user.is_bot:
                logger.info("pon: " + str(username))
                await message.answer_sticker(
                    sticker=get_pon_sticker())
        if  str(message.text).lower() == 'd:' or find_whole_word('вж')(str(message.text)):
            if not message.from_user.is_bot:
                logger.info("ВЖ: " + str(username))
                await message.answer_sticker(
                    sticker='CAACAgIAAxkBAAEGIDVjTi0-ZF0drKvP0zeUkCtD7QAB-WIAAs8DAALgeVIHt6ePD9s35_cqBA')
        if str(message.text) == '/start@Crocodile_Covid_Bot':
            if not message.from_user.is_bot:
                logger.info("start Crocodile_Covid_Bot: " + str(username))
                await message.reply_sticker(
                    sticker='CAACAgIAAxkBAAEFmZdi_kfHvMkYVkaYF3U03XvpLnLrUAAC4h4AAsevYUua8eZ4oiN5hCkE')
        if find_whole_word('genshin')(str(message.text)) or find_whole_word('геншин')(str(message.text)):
            if not message.from_user.is_bot:
                logger.info("genshin: " + str(username))
                # await message.reply_sticker(
                #    sticker='CAACAgIAAxkBAAEFpB5jA2hRcSZ0Voo1LpQpuLDjw2vixAACDRcAAmRKKUnevtb6fKAwdSkE')
        if find_whole_word('300')(str(message.text)) or find_whole_word('триста')(str(message.text)):
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
            if str(message.from_user.id) != OWNER_USER_ID:
                logger.info("Delete message: perm denied: " + str(message.from_user.id))
            else:
                logger.info("Delete message: try deleting message w text: " + str(message.reply_to_message.text))
                await bot.delete_message(chat_id=message.chat.id, message_id=message.reply_to_message.message_id)
        else:
            msg_id = message.get_args().strip()
            if not msg_id or len(msg_id) == 0:
                logger.info("Delete message: msg_id in message not found")
            else:
                if str(message.from_user.id) not in ADMIN_USER_IDS:
                    logger.info("Delete message: perm denied: " + str(message.from_user.id))
                else:
                    logger.info("Delete message: try deleting message w id: " + str(msg_id))
                    await bot.delete_message(chat_id=CAKE_CHAT_ID, message_id=int(msg_id))
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
            if str(message.from_user.id) not in ADMIN_USER_IDS:
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


@dp.message_handler(commands=['band'])
async def band(message: types.Message):
    logger.info("ban and delete message request")
    try:
        if await is_old_message(message):
            return
        await message.delete()
        if message.reply_to_message is not None:
            if str(message.from_user.id) not in ADMIN_USER_IDS:
                logger.info("Band: perm denied: " + str(message.from_user.id))
            else:
                logger.info("Band: try ban user: " + str(message.reply_to_message.from_user.id))
                await bot.restrict_chat_member(chat_id=message.chat.id,
                                               user_id=int(message.reply_to_message.from_user.id),
                                               permissions=ChatPermissions(can_send_messages=False))
                await bot.delete_message(chat_id=message.chat.id, message_id=message.reply_to_message.message_id)
        else:
            logger.info("Band: reply message not found")
    except Exception as e:
        logger.error('Failed to band user: ' + str(e))


@dp.message_handler(commands=['addpoints'])
async def add_points(message: types.Message):
    logger.info("add points request")
    try:
        if await is_old_message(message):
            return
        await message.delete()
        if message.reply_to_message is not None:
            if str(message.from_user.id) != OWNER_USER_ID:
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
            if str(message.from_user.id) not in ADMIN_USER_IDS:
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
                if str(message.from_user.id) not in ADMIN_USER_IDS:
                    logger.info("Mute: perm denied: " + str(message.from_user.id))
                else:
                    logger.info("Mute: try mute user: " + str(user_id))
                    until_date = (int(time.time()) + 3600)
                    await bot.restrict_chat_member(chat_id=CAKE_CHAT_ID, user_id=int(user_id),
                                                   permissions=ChatPermissions(can_send_messages=False),
                                                   until_date=until_date)
    except Exception as e:
        logger.error('Failed to mute user: ' + str(e))


@dp.message_handler(commands=['muted'])
async def muted(message: types.Message):
    logger.info("muted request")
    try:
        if await is_old_message(message):
            return
        await message.delete()
        if message.reply_to_message is not None:
            if str(message.from_user.id) not in ADMIN_USER_IDS:
                logger.info("muted: perm denied: " + str(message.from_user.id))
            else:
                seconds = int(message.get_args().strip())
                logger.info("muted: try muted user: " + str(message.reply_to_message.from_user.id) + " for " + str(
                    seconds) + " seconds")
                until_date = (int(time.time()) + seconds)
                await bot.restrict_chat_member(chat_id=message.chat.id,
                                               user_id=int(message.reply_to_message.from_user.id),
                                               permissions=ChatPermissions(can_send_messages=False),
                                               until_date=until_date)
                await bot.delete_message(chat_id=message.chat.id, message_id=message.reply_to_message.message_id)
        else:
            user_id = message.get_args().strip()
            if not user_id or len(user_id) == 0:
                logger.info("muted: user_id in message not found")
            else:
                if str(message.from_user.id) not in ADMIN_USER_IDS:
                    logger.info("muted: perm denied: " + str(message.from_user.id))
                else:
                    logger.info("muted: try mute user: " + str(user_id))
                    until_date = (int(time.time()) + 3600)
                    await bot.restrict_chat_member(chat_id=CAKE_CHAT_ID, user_id=int(user_id),
                                                   permissions=ChatPermissions(can_send_messages=False),
                                                   until_date=until_date)
    except Exception as e:
        logger.error('Failed to muted user: ' + str(e))


@dp.message_handler(commands=['unmute', 'unban'])
async def unmute(message: types.Message):
    logger.info("unmute request")
    try:
        if await is_old_message(message):
            return
        await message.delete()
        if message.reply_to_message is not None:
            if str(message.from_user.id) not in ADMIN_USER_IDS:
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
                if str(message.from_user.id) not in ADMIN_USER_IDS:
                    logger.info("Unmute: perm denied: " + str(message.from_user.id))
                else:
                    logger.info("Unmute: try mute user: " + str(user_id))
                    await bot.restrict_chat_member(chat_id=CAKE_CHAT_ID, user_id=int(user_id),
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
        if str(message.from_user.id) != OWNER_USER_ID:
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
        if str(message.from_user.id) != OWNER_USER_ID:
            logger.info("Say to cake message: perm denied: " + str(message.from_user.id))
        else:
            if message.reply_to_message is None:
                logger.info("Say to cake message: try say message w text: " + str(text))
                await bot.send_message(chat_id=CAKE_CHAT_ID, text=str(text))
            else:
                logger.info("Reply to cake  message: try repoly to message w text: " + str(
                    message.reply_to_message.text) + ", text: " + str(text))
                await bot.send_message(chat_id=CAKE_CHAT_ID, text=str(text),
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
        if str(message.from_user.id) != OWNER_USER_ID:
            logger.info("Check permissions: perm denied: " + str(message.from_user.id))
        else:
            logger.info("Check permissions: try check permissions...: ")
            member = await bot.get_chat_member(chat_id=CAKE_CHAT_ID, user_id=int(TOKEN.split(":")[0]))
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
            f"{new_member.get_mention(as_html=True)}, добро пожаловать! Располагайся 😳 P.S. Если ты новенький, то попытай счастья в рулетке /roulette :)",
            parse_mode=ParseMode.HTML,
        )
        await asyncio.sleep(60)
        await bot_message.delete()


@dp.message_handler(content_types=[types.ContentType.STICKER])
async def handle_sticker(message: types.Message):
    logger.info("Sticker file id: " + message.sticker.file_unique_id)
    try:
        if message.sticker.file_unique_id == 'AgADLCMAAqFd4Es':
            # xdd
            logger.info("Sticker: " + str(message.sticker.file_unique_id))
            await message.answer_sticker(
                sticker='CAACAgIAAxkBAAEGfuNje8MzLbr1c81ZIugn9I45A6fm0gACXRoAApJdYEtMTTimqH0G8ysE')
    except:
        pass
    try:
        if message.sticker.file_unique_id == 'AgADXRoAApJdYEs':
            # xdd
            logger.info("Sticker: " + str(message.sticker.file_unique_id))
            await message.answer_sticker(
                sticker='CAACAgIAAxkBAAEGfuNje8MzLbr1c81ZIugn9I45A6fm0gACXRoAApJdYEtMTTimqH0G8ysE')
    except:
        pass
    try:
        if message.sticker.file_unique_id == 'AgADgCMAAqzQ4Es':
            # xdd
            logger.info("Sticker: " + str(message.sticker.file_unique_id))
            await message.answer_sticker(
                sticker='CAACAgIAAxkBAAEGfuNje8MzLbr1c81ZIugn9I45A6fm0gACXRoAApJdYEtMTTimqH0G8ysE')
    except:
        pass
    try:
        if message.sticker.file_unique_id == 'AgADfxoAAjAf0Uk':
            # SHTO
            logger.info("Sticker: " + str(message.sticker.file_unique_id))
            await message.answer_sticker(
                sticker='CAACAgIAAxkBAAEGmN5jhSP4lTNbCyd6EQ56XhM7zeQbBwACfxoAAjAf0UnKR8QKFENRVSsE')
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

        #if int(points_bet) > 500:
        #    bot_m = await message.answer(
        #        message.from_user.get_mention(as_html=True) + ", ставка = максимум 500",
        #        parse_mode=ParseMode.HTML)
        #    logger.info("Duel, send message: " + str(bot_m.text))
        #    await message.delete()
        #    await asyncio.sleep(5)
        #    await bot_m.delete()
        #    logger.info("Duel: bet is max")
        #    return

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
        if not duel_roll_started or not duel_is_started:
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


@dp.message_handler(commands=['minestatus', 'ms'])
async def mine_status(message: types.Message):
    logger.info("minestatus request")
    try:
        try:
            if await is_old_message(message):
                return
            await message.delete()
        except Exception as e:
            logger.error('Failed minestatus: ' + str(e))
            return

        if str(message.chat.id) not in ATERNOS_ACCESS_IDS:
            return
        try:
            logger.info('aternos: restoring from session...')
            aternos = Client.restore_session()
        except Exception:
            logger.info('aternos: error, connect via creds...')
            aternos = Client.from_credentials(ATERNOS_LOGIN, ATERNOS_PASSWORD)
        aternos.save_session()
        servers = aternos.list_servers(cache=False)
        myserv = servers[0]
        for x in range(len(servers)):
            logger.info(servers[x].address)
            if ATERNOS_SENTRY_NAME in str(servers[x].address):
                myserv = servers[x]
        if myserv is None:
            await message.answer('Сервер не найден', parse_mode=ParseMode.HTML)
            return
        logger.info(myserv.status)
        await message.answer(message.from_user.get_mention(as_html=True) + ', статус сервера: ' + myserv.status + ' '
                             + get_emote_by_server_status(status=myserv.status) + '\nАдрес: ' + myserv.address + ', players: ' + str(myserv.players_list),
                             parse_mode=ParseMode.HTML)
    except Exception as e:
        await message.answer('Произошла ошибка при проверке статуса сервера', parse_mode=ParseMode.HTML)
        logger.error('Failed minestatus: ' + str(e))


@dp.message_handler(commands=['mcstart', 'mc'])
async def mine_start(message: types.Message):
    logger.info("mcstart request")
    try:
        try:
            if await is_old_message(message):
                return
            await message.delete()
        except Exception as e:
            logger.error('Failed minestatus: ' + str(e))
            return

        if str(message.chat.id) not in ATERNOS_ACCESS_IDS:
            return
        try:
            logger.info('aternos: restoring from session...')
            aternos = Client.restore_session()
        except Exception:
            logger.info('aternos: error, connect via creds...')
            aternos = Client.from_credentials(ATERNOS_LOGIN, ATERNOS_PASSWORD)
        aternos.save_session()
        servers = aternos.list_servers(cache=False)
        myserv = None
        for x in range(len(servers)):
            logger.info(servers[x].address)
            if ATERNOS_SENTRY_NAME in str(servers[x].address):
                myserv = servers[x]
        if myserv is None:
            await message.answer('Сервер не найден', parse_mode=ParseMode.HTML)
            return
        logger.info(myserv.status)
        if myserv.status == 'online':
            await message.answer(message.from_user.get_mention(as_html=True) +', сервер в данный момент запущен', parse_mode=ParseMode.HTML)
            return
        if myserv.status == 'starting' or myserv.status == 'preparing' or myserv.status == 'loading':
            await message.answer(message.from_user.get_mention(as_html=True) +', сервер запускается...', parse_mode=ParseMode.HTML)
            return
        if myserv.status == 'stopping' or myserv.status == 'saving':
            await message.answer(message.from_user.get_mention(as_html=True) +', сервер останавливается...', parse_mode=ParseMode.HTML)
            return
        status_message = await message.answer(message.from_user.get_mention(as_html=True) + ', начался запуск сервера, статус: '
                                              + myserv.status + ' ' + get_emote_by_server_status(status=myserv.status),
                             parse_mode=ParseMode.HTML)
        myserv.start()
        old_status = myserv.status
        while True:
            servers = aternos.list_servers(cache=False)
            loop_serv = None
            for x in range(len(servers)):
                logger.info(servers[x].address)
                if ATERNOS_SENTRY_NAME in str(servers[x].address):
                    loop_serv = servers[x]
            if loop_serv is None:
                return
            logger.info(loop_serv.status)
            if old_status != loop_serv.status:
                old_status = loop_serv.status
                await status_message.edit_text(message.from_user.get_mention(as_html=True) + ', начался запуск сервера, статус: '
                                               + loop_serv.status + ' ' + get_emote_by_server_status(status=loop_serv.status),
                                 parse_mode=ParseMode.HTML)
            if old_status == 'online':
                break
            await asyncio.sleep(10)
        servers = aternos.list_servers(cache=False)
        myserv = None
        for x in range(len(servers)):
            logger.info(servers[x].address)
            if ATERNOS_SENTRY_NAME in str(servers[x].address):
                myserv = servers[x]
        if myserv is None:
            await message.answer('Сервер не найден', parse_mode=ParseMode.HTML)
            return
        await status_message.answer(
            message.from_user.get_mention(as_html=True) + ', сервер запущен, статус: '
                + myserv.status + ' ' + get_emote_by_server_status(status=myserv.status),
            parse_mode=ParseMode.HTML)
    except Exception as e:
        await message.answer('Произошла ошибка при старте сервера', parse_mode=ParseMode.HTML)
        logger.error('Failed mcstart: ' + str(e))


def get_emote_by_server_status(status: str) -> str:
    if status == 'online':
        return '🟩'
    if status == 'offline':
        return '🟥'
    if status == 'stopping':
        return '🟧'
    if status == 'preparing':
        return '🟧'
    if status == 'loading':
        return '🟧'
    if status == 'starting':
        return '🟧'
    if status == 'saving':
        return '🟧'
    return ''


@dp.message_handler(content_types=[
    types.ContentType.VOICE,
    types.ContentType.VIDEO_NOTE
    ]
)
async def voice_message_handler(message: types.Message):
    logger.info("stt request")
    try:
        if str(message.chat.id) not in STT_ACCESS_IDS:
            return
        if await is_old_message(message):
            return
        if message.content_type == types.ContentType.VOICE:
            file_id = message.voice.file_id
        elif message.content_type == types.ContentType.VIDEO_NOTE:
            file_id = message.video_note.file_id
        else:
            return
        member = await message.chat.get_member(message.from_user.id)
        username = message.from_user.mention
        logger.info(
            "Stt request: from chat: " + str(message.chat.title) + ", user_name: " + str(
                username) + ", message: " + str(message.text) + ", message_id: " + str(
                message.message_id) + ", user_id: " + str(
                message.from_user.id) + ", chat_id: " + str(
                message.chat.id) + ", status: " + str(member.status))

        file = await bot.get_file(file_id)
        file_path = file.file_path
        file_on_disk = Path("voice_cache", f"{file_id}.tmp")
        await bot.download_file(file_path, destination=file_on_disk)

        text = await sync_to_async(stt.audio_to_text)(file_on_disk)
        if text:
            logger.info("Stt request: result: " + text )
            await message.reply("Я попытался разобрать текст:\n\n" + text)
        os.remove(file_on_disk)
    except Exception as e:
        logger.error('Failed stt: ' + str(e))
        os.remove(file_on_disk)



@dp.channel_post_handler(content_types=[
    types.ContentType.VOICE,
    types.ContentType.VIDEO_NOTE,
    ]
)
async def post_handler(message: types.Message) -> None:
    try:
        if await is_old_message(message):
            return
        if str(message.chat.id) != VOLJ_CHILL_CHANNEL_ID:
            return
        logger.info(
            "New post: from chat: " + str(message.chat.title)+", channel id: " + str(message.chat.id))
        if message.content_type == types.ContentType.VOICE:
            logger.info("New post: content_type: " + str(message.content_type))
        elif message.content_type == types.ContentType.VIDEO_NOTE:
            logger.info("New post: content_type: " + str(message.content_type))
        else:
            return
        logger.info("New post: start forwarding...")
        f_message = await message.forward(chat_id=VOLJ_CHILL_CHAT_ID)
        await voice_message_handler(f_message)
    except Exception as e:
        logger.error('New post: ' + str(e))


@dp.message_handler(commands=['dmt'])
async def demotivation_message_handler(reply_message: types.Message):
    logger.info("demotivation request")
    file_on_disk = None
    try:
        if await is_old_message(reply_message):
            return
        if reply_message.reply_to_message is None:
            bot_message = await reply_message.reply(
                "Ответьте командой на сообщение с картинкой или gif анимацией",
                parse_mode=ParseMode.HTML,
            )
            await asyncio.sleep(3)
            await reply_message.delete()
            await bot.delete_message(chat_id=bot_message.chat.id, message_id=bot_message.message_id)
            return
        message = reply_message.reply_to_message
        file_ext = None
        if message.content_type == types.ContentType.ANIMATION:
            file_id = message.animation.file_id
            print(message.animation.file_name)
            file_ext='.mp4'
        elif message.content_type == types.ContentType.PHOTO:
            file_id = message.photo[len(message.photo)-1].file_id
            file_ext='.jpg'
        else:
            bot_message = await reply_message.reply(
                "Ответьте командой на сообщение с картинкой или gif анимацией",
                parse_mode=ParseMode.HTML,
            )
            await asyncio.sleep(3)
            await reply_message.delete()
            await bot.delete_message(chat_id=bot_message.chat.id, message_id=bot_message.message_id)
            return
        args = reply_message.get_args().strip()
        text = None
        if args and len(args) != 0:
            text = args
        member = await message.chat.get_member(message.from_user.id)
        username = message.from_user.mention
        logger.info(
            "demotivation request: from chat: " + str(message.chat.title) + ", user_name: " + str(
                username) + ", message: " + str(message.text) + ", message_id: " + str(
                message.message_id) + ", user_id: " + str(
                message.from_user.id) + ", chat_id: " + str(
                message.chat.id) + ", status: " + str(member.status))

        file = await bot.get_file(file_id)
        file_path = file.file_path
        file_on_disk = Path("image_cache", f"{file_id}{file_ext}")
        await bot.download_file(file_path, destination=file_on_disk)
        input_file = f"image_cache/{file_id}{file_ext}"
        output_file = f"image_cache/result_{file_id}{file_ext}"
        p_func = functools.partial(degenerator.generate_demotivator, input_file, output_file, text)
        await asyncio.get_running_loop().run_in_executor(None, p_func)
        result_media = open(f"image_cache/result_{file_id}{file_ext}", 'rb')
        if file_ext == '.jpg':
            await reply_message.reply_photo(photo=result_media)
        else:
            await reply_message.reply_animation(animation=result_media)
        os.remove(f"image_cache/result_{file_id}{file_ext}")
        os.remove(file_on_disk)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('Failed demotivation: ' + str(e) + ", line: " + str(exc_tb.tb_lineno))
        if file_on_disk is not None and file_on_disk.exists():
            os.remove(file_on_disk)


@dp.message_handler(commands=['anime'])
async def anime_message_handler(reply_message: types.Message):
    logger.info("anime request")
    file_on_disk = None
    sticker = None
    try:
        if await is_old_message(reply_message):
            return
        if reply_message.reply_to_message is None:
            bot_message = await reply_message.reply(
                "Ответьте командой на сообщение с картинкой, содержащее лицо",
                parse_mode=ParseMode.HTML,
            )
            await asyncio.sleep(3)
            await reply_message.delete()
            await bot.delete_message(chat_id=bot_message.chat.id, message_id=bot_message.message_id)
            return
        message = reply_message.reply_to_message
        file_ext = None
        if message.content_type == types.ContentType.PHOTO:
            file_id = message.photo[len(message.photo)-1].file_id
            file_ext='.jpg'
        else:
            bot_message = await reply_message.reply(
                "Ответьте командой на сообщение с картинкой, содержащее лицо",
                parse_mode=ParseMode.HTML,
            )
            await asyncio.sleep(3)
            await reply_message.delete()
            await bot.delete_message(chat_id=bot_message.chat.id, message_id=bot_message.message_id)
            return
        member = await message.chat.get_member(message.from_user.id)
        username = message.from_user.mention
        logger.info(
            "anime request: from chat: " + str(message.chat.title) + ", user_name: " + str(
                username) + ", message: " + str(message.text) + ", message_id: " + str(
                message.message_id) + ", user_id: " + str(
                message.from_user.id) + ", chat_id: " + str(
                message.chat.id) + ", status: " + str(member.status))
        sticker = await message.reply_sticker(sticker=get_search_sticker())
        file = await bot.get_file(file_id)
        file_path = file.file_path
        file_on_disk = Path("anime_qq/image_cache", f"{file_id}{file_ext}")
        await bot.download_file(file_path, destination=file_on_disk)
        input_file = f"anime_qq/image_cache/{file_id}{file_ext}"
        output_file = f"anime_qq/image_cache/result_{file_id}{file_ext}"
        await sync_to_async(anime_qq.photo_to_anime)(input_file, output_file)
        result_media = open(f"anime_qq/image_cache/result_{file_id}{file_ext}", 'rb')
        await sticker.delete()
        sticker = None
        await reply_message.reply_photo(photo=result_media)
        os.remove(f"anime_qq/image_cache/result_{file_id}{file_ext}")
        os.remove(file_on_disk)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('Failed anime: ' + str(e) + ", line: " + str(exc_tb.tb_lineno))
        bot_message = await message.reply(
                    "Произошла ошибка : " + str(e),
                    parse_mode=ParseMode.HTML,
        )
        if sticker:
            await sticker.delete()
        if file_on_disk is not None and file_on_disk.exists():
            os.remove(file_on_disk)


@dp.message_handler(commands=['weather', 'w'])
async def handle_weather(message: types.Message):
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
            logger.info('Weather, city: ' + city)
            res = await weather.get_weather(city)
            await message.reply(res, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error('Failed to get weather: ' + str(e))
        bot_message = await message.reply(
            "Произошла ошибка при получении погоды",
            parse_mode=ParseMode.HTML,
        )
        await asyncio.sleep(3)
        await message.delete()
        await bot_message.delete()


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


def get_pon_sticker():
    pon_sticker = [
        "CAACAgIAAxkBAAEHJ7NjuRIy1XfdXOt60AX9oaA2Bh6UNwACMh0AAlsmkUumTv__sD7DnC0E",
        "CAACAgIAAxkBAAEHJ7VjuRI1wcJ7rSQzpjrywaDVyI4QuwACHxoAArBEmUuxVJmB16VUJS0E",
        "CAACAgIAAxkBAAEHJ7djuRJH7eBllwOgiGQdqWFK_kzokwACTxcAAvtAmEurg6WhIQV7ty0E",
        "CAACAgIAAxkBAAEHJ7ljuRJKp7v-1oWiLH6GxNKtlEvrfAACcBUAAluGwUsQDkQr6N7gji0E",
        "CAACAgIAAxkBAAEHJ7tjuRJM6dYLjJSI_tMYL3BP-jQgHAACMhUAAqezwEtR_5Pu2L5JyC0E",
        "CAACAgIAAxkBAAEHJ71juRJPqXBG1l1bCcA0_QABiF2J8SMAAmoYAAKl2MBLPcez96nf_fotBA",
        "CAACAgIAAxkBAAEHJ79juRJSpg-bjEQoye85a0-rizAvqQAClBwAAvMwuUnXj8oRV7nk9y0E",
        "CAACAgIAAxkBAAEHJ8FjuRJUCTlZvYdb89_VGQ2gvb5-CgACRRsAAl5XkUoOcaSH0AZacS0E",
        "CAACAgIAAxkBAAEHJ8NjuRJWB7gLzxAhNbRWBmaw-vFF6AAC5xYAAjIWmErhozuWys4vaC0E",
        "CAACAgIAAxkBAAEHJ8VjuRJZj-3NzVtjOJNZumP2QMCrGgAC-xgAAgm-6UrL_L-7Ss6M3S0E",
        "CAACAgIAAxkBAAEHJ8djuRJbKvGhrNAXkIbDZPwt13oa5wAClRwAAmAI-UrPZfSJhHshGy0E",
        "CAACAgIAAxkBAAEHJ2VjuRHGUerTQzKslQLmRhZO9BRsywACaRQAAknV4UqUqfiTpOkq0C0E",
        "CAACAgIAAxkBAAEHJ2djuRHJYlK6Wf8D9TUpY6MNu8vrBgACcxkAAhFf2UouAAG2caPV3zstBA",
        "CAACAgIAAxkBAAEHJ2ljuRHKU3u-FaGw6oBNpoIyW1428gACUhsAAmEa4Uq7puOnCHZQsS0E",
        "CAACAgIAAxkBAAEHJ2tjuRHM0gzt8-TgKIYW8aAUKpZHFAACbhsAAhR84UrMCV069wjKry0E",
        "CAACAgIAAxkBAAEHJ21juRHPxYTaJie9rbtmSn2gKU0gfwACYhoAAn122Uqj5Fu4Q04QDS0E",
        "CAACAgIAAxkBAAEHJ29juRHRIveqJYWnu8PlGjIgwjJNhAACwRoAApbw2EqyeALX6qX7Fy0E",
        "CAACAgIAAxkBAAEHJ3FjuRHUKcJaiA80z5rrUjC5DZglLwACjRYAAlGw4Upw79yJW33cgy0E",
        "CAACAgIAAxkBAAEHJ3NjuRHWG7ESLC60B2ZdDE8LOyVPdQACgCcAAnYx2EqT3Kji6FqtMy0E",
        "CAACAgIAAxkBAAEHJ3VjuRHZaQz39qvjw0HSd5dxyuZ6dAACrhQAAguO4Eo7KGAgkMiSrC0E",
        "CAACAgIAAxkBAAEHJ3djuRHbBsPFj_BngpDs8xcGfnvSpgAC4BcAAqyx4Ure85hUk0Owny0E",
        "CAACAgIAAxkBAAEHJ3ljuRHeQRdUuVQxfpOhJ5FadRdUSwAC2hUAArhMGUuib-zCcumAZC0E",
        "CAACAgIAAxkBAAEHJ3tjuRHgK9rLEbE43gheLR9KMAQmEAACkBgAAko8EEtZVtqffYZtGC0E",
        "CAACAgIAAxkBAAEHJ31juRHjZQn7wTGcJjcRaoTAdvs1eAACAhsAAqOLGEtxqbC_159d5S0E",
        "CAACAgIAAxkBAAEHJ39juRHmWx4FvlyfXz4uNYWQICiXBQACNBYAAmOfIUt1fDiSVYyw4S0E",
        "CAACAgIAAxkBAAEHJ4FjuRHoQtasIeQFNwj88WnkXQVPaAACfBUAAnB5IUvVTXxo_6DUci0E",
        "CAACAgIAAxkBAAEHJ4NjuRHrzKphRDKl3g9veV85y0S1TgAC3BMAAlbOIUuYnlS2L3K7FS0E",
        "CAACAgIAAxkBAAEHJ4VjuRHtxO-v1rpvCj_gSOlfUHTQPAAC5xQAAsV7IEtjlYYQNJz5Ci0E",
        "CAACAgIAAxkBAAEHJ4djuRHv4gAB5qW7HO7-ze9AopHst7IAAtEUAAKGqiBLen3ouD2B09ItBA",
        "CAACAgIAAxkBAAEHJ4ljuRHyl0NKEJ5_YuHkHklWmL3oOAACNhgAAg-LGUuwC82Jfq-sUC0E",
        "CAACAgIAAxkBAAEHJ4tjuRH05EJe3fddBZ_OReHiKeD1iwAC8xcAAuHfIEuMI_h8YtMrky0E",
        "CAACAgIAAxkBAAEHJ41juRH3BsOwxXPXmJemeGAz1HYH-AACXBYAAsHAIUu13uxwEb0j6i0E",
        "CAACAgIAAxkBAAEHJ49juRH6J_RfQz_M-pSPJXTb_LvWcAACDxYAAubqGUtNFxMnsNIYSS0E",
        "CAACAgIAAxkBAAEHJ5FjuRH8Ev3ILsLNFRi8B76PX4_72QACfRIAAhn3IEtHqdOQin-J4y0E",
        "CAACAgIAAxkBAAEHJ5NjuRIAAdo9sdJNIcsHlPEWHVUE6C8AAkESAAKqOSFLXCYFDpEO118tBA",
        "CAACAgIAAxkBAAEHJ5VjuRICbp5K6JvlDyWyLw4pDvHtEgACORkAAl7gOUuq5WFbkGJZ9C0E",
        "CAACAgIAAxkBAAEHJ5djuRIGi9hjVT-GGS0QSvgHsg03zgACuBsAAjebQEsM4J67scsLTS0E",
        "CAACAgIAAxkBAAEHJ5ljuRII1NtG2JVQMgRwaBaosiG_JQACrhUAAj3wSEv3PAMhx0Ko7i0E",
        "CAACAgIAAxkBAAEHJ5tjuRILAAHFvZ6o9ZzQfDr3Z0owJ5IAAv8WAAJvrGFLN5dT7Zu1KlMtBA",
        "CAACAgIAAxkBAAEHJ51juRIOHqE9uC2wC8DZ0jZOqt0YzwACIhoAAnbOYUspZwWlehPEsC0E",
        "CAACAgIAAxkBAAEHJ59juRIUO30IZGvuR8E2gfNIKF1AawACthcAAsQYYEs9iLaVJDn3gS0E",
        "CAACAgIAAxkBAAEHJ6FjuRIYBdgng_JYUL_lBKDYRMk_rwACeBkAAvjRYUtYgKOqHb2sgi0E",
        "CAACAgIAAxkBAAEHJ6VjuRIeKj3f272SiWo7x2HruWUrTAACORkAAmDSYUuUlKE19QlZCi0E",
        "CAACAgIAAxkBAAEHJ6djuRIiznUtPndjq6luU1rwt0yz5AACChkAAnMOcEtxJDDRL_v7Ry0E",
        "CAACAgIAAxkBAAEHJ6ljuRIlZjzlh0YKE9a7e2sLecawUgAC1BkAAuDhmEvQtwx_hCQsnS0E",
        "CAACAgIAAxkBAAEHJ6tjuRIo7hqd7wEb4mFFwCla9bbqJQACpBsAApjdmEvTWxJ9OXc2uy0E",
        "CAACAgIAAxkBAAEHJ61juRIqKEDMFoGyVyhrM2jFZtDB-wACzBYAAtmhmEsDblZSAgoQyS0E",
        "CAACAgIAAxkBAAEHJ69juRItV2OAbEdnmKM2H4zfq9eUogACtRcAArbDmUtq0KeQcciVgS0E",
        "CAACAgIAAxkBAAEHJ7FjuRIvuny1aFQ0pnHfj5_su4lzjQACOhsAAoaMmEtM641BJNIOnS0E",
        "CAACAgIAAxkBAAEGgMJjfKIcIL6W7W_ppolriLR9aV1AcAACuB8AAkK98UgFWvmoqa7OYCsE",
    ]
    return random.choice(pon_sticker)


def get_search_sticker():
    search_sticker = [
        "CAACAgIAAxkBAAEHKjpjucklxBly-bkdZ4lAKAHxKcTDSQACCyoAAuPl0Uk4rWp3Lw5d1S0E",
        "CAACAgIAAxkBAAEHKjxjuckoCXVxhSTIBtzXXlWsLTmKvAACeSoAAsFFyUncs5PojEhUwC0E",
        "CAACAgIAAxkBAAEHKmJjudALk8SchSVF7h-XX0kKQ2fGIwAC5yMAAhz20EnzTgw_iUxmYi0E",
        "CAACAgIAAxkBAAEHKmZjudBK_DOAjnAtgmhxWwbxOiM1gQACNSsAAhPXyEm-LYMjiOoldy0E",
    ]
    return random.choice(search_sticker)


def find_whole_word(w):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search


if __name__ == '__main__':
    main()
