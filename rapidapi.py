import requests
import json
import re
import auxiliary
from settings import *
from loader import Users


def request_to_api(url: str, params: dict[str, str], timeout: int = 20) -> requests.Response:
    """
    Базовая функция запроса к API
    :param url: строка URL адреса
    :param params: словарь с параметрами запроса
    :param timeout: время ожидания ответа
    :return: объект ответа Response
    """
    response = requests.get(url, headers=headers, params=params, timeout=timeout)
    response.raise_for_status()
    return response


def api_get_locate(query: str, locale: str = LOCALE, currency: str = CURRENCY) -> dict[str, str]:
    """
    Запрос к API Hotels для получения словаря городов с похожим названием

    :param query: Название города
    :param locale: Язык
    :param currency: Валюта
    :return: Словарь {ID города: название города}
    """

    url = URL_HOST + URL_PATHS['locations']
    querystring = {"query": query, "locale": locale, "currency": currency}
    response = request_to_api(url, querystring)
    pattern = r'(?<="CITY_GROUP",).+?[\]]'
    find = re.search(pattern, response.text)
    find = json.loads(f"{{{find[0]}}}")
    result = dict()
    for cities in find['entities']:
        if cities['type'] == 'CITY':
            result[cities['destinationId']] = auxiliary.remove_tags(cities['caption'])
    return result


# todo правильно ли делаю аннотацию? я импортировал класс Users только для этого
def api_get_hotels(user: Users, page_number: str = '1', page_size: str = "25",
                   adults1: str = '1', locale: str = LOCALE,
                   currency: str = CURRENCY) -> list[dict[str, str]]:
    """
    Запрос к API Hotels для получения списка словарей отелей по ID города
    :param user: объект класса Users
    :param page_number: номер страницы в поисковой выдачи
    :param page_size: размер страницы в поисковой выдачи
    :param adults1: количество мест
    :param locale: язык
    :param currency: валюта
    :return: Список словарей с информацией об отелях
    """
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

    find = json.loads(f"{{{find[0]}}}")
    result = list()
    for hotel in find['results']:
        hotel_info = {
            'hotel_name': hotel['name'],
            'hotel_id': hotel['id'],
            'distance_from_center': hotel['landmarks'][0]['distance'],
        }
        try:
            # иногда streetAddress нет
            hotel_info['address'] = hotel['address']['streetAddress']
        except KeyError as ex:
            print(f'{type(ex).__name__} {ex} {hotel["id"]}')
            hotel_info['address'] = ' - '
        try:
            # иногда ratePlan нет
            hotel_info['price'] = hotel['ratePlan']['price']['current'].replace(',', ' ')
        except KeyError as ex:
            print(f'{type(ex).__name__} {ex} {hotel["id"]}')
            hotel_info['price'] = ' - '
        result.append(hotel_info)
    return result


def api_get_photos(hotel_id: str, max_room_images: int = 0, max_hotel_images: int = 3) -> list[str]:
    """
    Запрос к API Hotels для получения списка URL фотографий отеля.

    В URL фото, полученных от API функция вставляет код размера, также полученный от API,
    размер фото минимальный (чаще всего Z).
    :param hotel_id: ID отеля
    :param max_room_images: максимальное количество фотографий комнат
    :param max_hotel_images: максимальное количество общих фотографий отеля
    :return: список URL фотографий
    """
    url = URL_HOST + URL_PATHS['photos']
    querystring = {"id": hotel_id}
    response = request_to_api(url, querystring)

    pattern = r'"hotelImages".+?(?=,"featuredImageTrackingDetails")'
    find = re.search(pattern, response.text)

    find = json.loads(f"{{{find[0]}}}")
    hotel_image_count = 0
    room_image_count = 0
    url_all_images = []
    for hotel_image in find['hotelImages']:
        if hotel_image_count < max_hotel_images:
            try:
                hotel_image_url = hotel_image['baseUrl'].replace(
                    '{size}',
                    hotel_image['sizes'][0]['suffix']
                )
                url_all_images.append(hotel_image_url)
                hotel_image_count += 1
            except (KeyError, TypeError) as ex:
                print(f'{type(ex).__name__} {ex}')
        else:
            break
    for room in find['roomImages']:
        if room_image_count < max_room_images:
            try:
                room_image_url = room['images'][0]['baseUrl'].replace(
                    '{size}',
                    room['images'][0]['sizes'][0]['suffix']
                )
                url_all_images.append(room_image_url)
                room_image_count += 1
            except (KeyError, TypeError) as ex:
                print(f'{type(ex).__name__} {ex}')
        else:
            break
    return url_all_images

