import datetime
from dotenv import load_dotenv
import os
import requests
from aiogram.utils.markdown import hbold

load_dotenv()
weather_api = os.getenv("OPENWEATHERMAP_API")


async def get_weather(city: str):
    date = datetime.datetime.now().strftime('%d.%m.%Y')
    code_to_smile = {
        "Clear": "\U00002600 Ясно",
        "Clouds": "\U00002601 Облачно",
        "Rain": "\U00002614 Дождь",
        "Drizzle": "\U00002614 Дождь",
        "Thunderstorm": "\U000026A1 Гроза",
        "Snow": "Снег \U0001F328",
        "Mist": "Туман \U0001F32B"
    }
    data_weather = requests.get(
        f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api}&units=metric').json()

    if data_weather['cod'] == '404':
        return 'Не найдено'
    weather_description = data_weather['weather'][0]['main']

    if weather_description in code_to_smile:
        wd = code_to_smile[weather_description]
    else:
        wd = '-'

    city = data_weather['name']
    feels_like = round(data_weather['main']['feels_like'])
    temp = round(data_weather['main']['temp'])
    temp_max = round(data_weather['main']['temp_max'])
    temp_min = round(data_weather['main']['temp_min'])
    humidity = data_weather['main']['humidity']
    sunrise = datetime.datetime.fromtimestamp(data_weather['sys']['sunrise'])
    sunset = datetime.datetime.fromtimestamp(data_weather['sys']['sunset'])
    forecast = (f'{hbold(city)} - {hbold(date)}\n'
                          f'️{hbold(wd)}\n'
                          f'🌡️ {hbold("Температура")}: {hbold(temp)}℃\n'
                          f'🌡️ {hbold("Ощущается как")}: {hbold(feels_like)}℃\n'
                          f'🌡️ {hbold("Максимальная температура")}: {hbold(temp_max)}℃\n'
                          f'🌡️ {hbold("Минимальная температура")}: {hbold(temp_min)}℃\n'
                          f'💧 {hbold("Влажность")}: {hbold(humidity)}%\n'
                          f'🌅 {hbold("Рассвет")}: {hbold(sunrise.strftime("%H:%M"))}\n'
                          f'🌇 {hbold("Закат")}: {hbold(sunset.strftime("%H:%M"))}')
    return forecast
