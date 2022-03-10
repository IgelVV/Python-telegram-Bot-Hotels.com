import requests
import json
import re
import auxiliary
from settings import *


def request_to_api(url, params, timeout=20):
    """
    Базовая функция запроса к API
    :param url:
    :param params:
    :param timeout:
    :return:
    """
    try:
        response = requests.get(url, headers=headers, params=params, timeout=timeout)
        if response.status_code == requests.codes.ok:
            return response
    except Exception as ex:
        print(ex)


# перенести локализацию в settings
def api_get_locate(query, locale='ru_RU', currency='RUB'):
    """
    Запрос к API Hotels для получения списка городов с похожим названием

    :param query: Название города
    :param locale:
    :param currency:
    :return: Список словарей {название города; ID города}
    """

    url = URL_HOST + URL_PATHS['locations']
    querystring = {"query": query, "locale": locale, "currency": currency}
    response = request_to_api(url, querystring)

    pattern = r'(?<="CITY_GROUP",).+?[\]]'
    find = re.search(pattern, response.text)  #todo AttributeError: 'NoneType' object has no attribute 'text'
    if find:
        find = json.loads(f"{{{find[0]}}}")
        result = [{
            'city_name': auxiliary.remove_tags(cities['caption']),
            'destination_id': cities['destinationId']
        }
            for cities in find['entities']
            if cities['type'] == 'CITY']
        return result
    else:
        return None


def api_get_hotels(user, page_number='1', page_size="25",
                   adults1='1', locale='ru_RU', currency='RUB'):
    url = URL_HOST + URL_PATHS['properties']
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
        sort_order = QUERY_PARAMETERS["sortOrder"]["lowprice"]
        querystring["sortOrder"] = sort_order
    elif user.command == 'highprice':
        sort_order = QUERY_PARAMETERS["sortOrder"]['highprice']
        querystring["sortOrder"] = sort_order
    elif user.command == 'bestdeal':
        sort_order = QUERY_PARAMETERS["sortOrder"]['bestdeal']
        price_min = user.price_range[0]
        price_max = user.price_range[1]
        querystring["sortOrder"] = sort_order
        querystring["priceMin"] = price_min
        querystring["priceMax"] = price_max

    response = request_to_api(url, querystring)

    pattern = r'"results".+?(?=,"pagination")'
    find = re.search(pattern, response.text)
    if find:
        find = json.loads(f"{{{find[0]}}}")
        result = list()
        for hotel in find['results']:
            hotel_info = {
                'hotel_name': hotel['name'],
                'hotel_id': hotel['id'],
                'distance_from_center': hotel['landmarks'][0]['distance']
            }
            try:
                hotel_info['price'] = hotel['ratePlan']['price']['current'].replace(',', ' ') # иногда ratePlan нет
            except KeyError as e:
                print(f'KeyError {e} {hotel["id"]}')
                hotel_info['price'] = ' - '
            result.append(hotel_info)
        return result
    else:
        return None


def api_get_photos(hotel_id: str, room_images=0, hotel_images=3):
    # размер фото минимальный (чаще всего Z)
    url = URL_HOST + URL_PATHS['photos']
    querystring = {"id": hotel_id}
    response = request_to_api(url, querystring)

    pattern = r'"hotelImages".+?(?=,"featuredImageTrackingDetails")'
    find = re.search(pattern, response.text)   # todo AttributeError: 'NoneType' object has no attribute 'text'
    if find:
        find = json.loads(f"{{{find[0]}}}")
        hotel_image_count = 1
        room_image_count = 1
        url_all_images = []
        for hotel_image in find['hotelImages']:
            if hotel_image_count <= hotel_images:
                hotel_image_url = hotel_image['baseUrl'].replace(
                    '{size}',
                    hotel_image['sizes'][0]['suffix']
                )
                url_all_images.append(hotel_image_url)
                hotel_image_count += 1
            else:
                break
        for room in find['roomImages']:
            if room_image_count <= room_images:
                room_image_url = room['images'][0]['baseUrl'].replace(
                    '{size}',
                    room['images'][0]['sizes'][0]['suffix']
                )
                url_all_images.append(room_image_url)
                room_image_count += 1
            else:
                break
        return url_all_images
    else:
        return None
