import string
import xml.etree.ElementTree as ET
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

import requests

apiSigns = {
    "Овен": "aries",
    "Телец": "taurus",
    "Близнецы": "gemini",
    "Рак": "cancer",
    "Лев": "leo",
    "Дева": "virgo",
    "Весы": "libra",
    "Скорпион": "scorpio",
    "Стрелец": "sagittarius",
    "Козерог": "capricorn",
    "Водолей": "aquarius",
    "Рыбы": "pisces"
}

apiDays = {
    "Сегодня": "today",
    "Завтра": "tomorrow",
    "Вчера": "yesterday"
}


def request():
    response = requests.get("https://ignio.com/r/export/utf/xml/daily/com.xml").text
    return ET.fromstring(response)


def getHoro(horoscope, sign):
    level = sign + "/" + "today"
    date = None
    for tag in horoscope.findall('date'):
        date = tag.get('today')
    for tag in horoscope.findall(level):
        return ' ' + date + ':' + tag.text
