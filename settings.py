# todo перенести сюда все параметры запросов к API
#  и все сообщения пользователю (в зависимости от языка)
from loader import RAPIDAPI_KEY

URL_HOST = 'https://hotels4.p.rapidapi.com/'
URL_PATHS = {
    'locations': 'locations/v2/search',
    'properties': 'properties/list',
    'photos': 'properties/get-hotel-photos'
}

headers = {
    'x-rapidapi-host': "hotels4.p.rapidapi.com",
    'x-rapidapi-key': RAPIDAPI_KEY
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
