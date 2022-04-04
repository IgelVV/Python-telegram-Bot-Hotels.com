import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
RAPID_API_KEY = os.getenv('RAPID_API_KEY')
DEFAULT_COMMANDS = (
    ('start', "Начало работы"),
    ('lowprice', "Поиск самых дешевых отелей"),
    ('highprice', "Поиск самых дорогих отелей"),
    ('bestdeal', "Поиск с расширенными параметрами"),
    ('history', "История запросов"),
    ('help', "Список команд")
)

URL_HOST = 'https://hotels4.p.rapidapi.com/'
URL_PATHS = {
    'locations': 'locations/v2/search',
    'properties': 'properties/list',
    'photos': 'properties/get-hotel-photos'
}

headers = {
    'x-rapidapi-host': "hotels4.p.rapidapi.com",
    'x-rapidapi-key': RAPID_API_KEY
}

QUERY_PARAMETERS = {
    "sortOrder": {
        "lowprice": "PRICE",
        "highprice": "PRICE_HIGHEST_FIRST",
        "bestdeal": "DISTANCE_FROM_LANDMARK"
                  }
}

LOCALE = 'ru_RU'

CURRENCY = 'RUB'
