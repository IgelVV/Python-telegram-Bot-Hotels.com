# дочерний http://rapidapi.py или, может, как-нибудь иначе?
# Главное чтобы подходило по смыслу.
#
# В нем создается класс для работы с API и в нем делаются все запросы к API;

import requests
import re
import json
from loader import RAPIDAPI_KEY

url_host = 'https://hotels4.p.rapidapi.com/'
url_paths = {
    'locations': 'locations/v2/search',
    'properties': 'properties/list',
    'photos': 'properties/get-hotel-photos'
             }

headers = {
    'x-rapidapi-host': "hotels4.p.rapidapi.com",
    'x-rapidapi-key': RAPIDAPI_KEY
    }


def request_to_api(url, params, timeout=20):
    try:
        response = requests.get(url, headers=headers, params=params, timeout=timeout)
        if response.status_code == requests.codes.ok:
            return response
    except Exception as ex:
        print(ex)


def api_get_locate(query, locale='ru_RU', currency='RUB'):
    """
    Запрос к API Hotels для получения списка городов с похожим названием

    :param query: Название города
    :param locale:
    :param currency:
    :return: Список словарей {название города; ID города}
    """

    url = url_host + url_paths['locations']
    querystring = {"query": query, "locale": locale, "currency": currency}
    response = request_to_api(url, querystring)

    pattern = r'(?<="CITY_GROUP",).+?[\]]'
    find = re.search(pattern, response.text)
    if find:
        find_dict = json.loads(f"{{{find[0]}}}")
        result = [{
            'city_name': remove_tags(cities['caption']),
            'destination_id': cities['destinationId']
        }
                  for cities in find_dict['entities']
                  if cities['type'] == 'CITY']
        return result


def api_get_hotels(user, page_number='1', page_size="25",
                   adults1='1', locale='ru_RU', currency='RUB'):
    url = url_host + url_paths['properties']
    destination_id = user.city_id
    check_in = user.check_in
    check_out = user.check_out

    querystring = {
        "destinationId": destination_id,
        "pageNumber": page_number,
        "pageSize": page_size,
        "checkIn": check_in,
        "checkOut": check_out,
        "adults1": adults1,
        "locale": locale,
        "currency": currency
    }

    if user.command == 'lowprice':
        sort_order = "PRICE"  # todo from settings
        querystring["sortOrder"] = sort_order
    elif user.command == 'highprice':
        sort_order = "PRICE_HIGHEST_FIRST"
        querystring["sortOrder"] = sort_order
    elif user.command == 'bestdeal':
        sort_order = "DISTANCE_FROM_LANDMARK"
        price_min = user.price_range[0]  # todo to str
        price_max = user.price_range[1]
        querystring["sortOrder"] = sort_order
        querystring["priceMin"] = price_min
        querystring["priceMax"] = price_max

    response = request_to_api(url, querystring)

    pattern = r'"results".+?(?=,"pagination")'
    find = re.search(pattern, response.text)
    if find:
        find_dict = json.loads(f"{{{find[0]}}}")
        result = [{
            'hotel_name': hotels['name'],
            'hotel_id': hotels['id'],
            'distance_from_center': hotels['landmarks'][0]['distance']
        }
                  for hotels in find_dict['results']]
        return result


def remove_tags(text):
    """
    Очистка текста от HTML тегов.
    :param text:
    :return:
    """
    html_text_regex = re.compile(r'<[^>]+>')
    return html_text_regex.sub('', text)


def find_number(text):
    """

    :param text:
    :return:
    """
    result = re.search('[0-9]+', text)
    if result is not None:
        number_str = result.group(0)
        number = int(number_str)
    else:
        number = None
    return number


def price_range_from_text(text):
    list_of_numb_str = re.findall('[0-9]+', text)
    list_of_numb_int = [int(numb) for numb in list_of_numb_str]
    list_of_numb_int.sort()
    return list_of_numb_int


