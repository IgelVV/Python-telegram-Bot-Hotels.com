import requests
import re
import json
from loader import RAPIDAPI_KEY

#  Где хранить эти данные? Нужно ли записывать большими буквами URL_HOST?
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
    else:
        return None


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
            'hotel_name': hotel['name'],
            'hotel_id': hotel['id'],
            'distance_from_center': hotel['landmarks'][0]['distance'],
            'price': hotel['ratePlan']['price']['current'].replace(',', ' ')
        }
            for hotel in find_dict['results']]
        return result
    else:
        return None


def api_get_photos(hotel_id: str, room_images=0, hotel_images=3):
    # размер фото минимальный (чаще всего Z)
    url = url_host + url_paths['photos']
    querystring = {"id": hotel_id}
    response = request_to_api(url, querystring)

    pattern = r'"hotelImages".+?(?=,"featuredImageTrackingDetails")'
    find = re.search(pattern, response.text)
    if find:
        find_dict = json.loads(f"{{{find[0]}}}")
        hotel_image_count = 1
        room_image_count = 1
        image_url_lst = []
        for i_hotel_image in find_dict['hotelImages']:
            if hotel_image_count <= hotel_images:
                hotel_image_url = i_hotel_image['baseUrl'].replace(
                    '{size}',
                    i_hotel_image['sizes'][0]['suffix']
                )
                image_url_lst.append(hotel_image_url)
                hotel_image_count += 1
            else:
                break
        for i_room in find_dict['roomImages']:
            if room_image_count <= room_images:
                room_image_url = i_room['images'][0]['baseUrl'].replace(
                    '{size}',
                    i_room['images'][0]['sizes'][0]['suffix']
                    # todo переписать, иногда присылает одинаковые фотки
                )
                image_url_lst.append(room_image_url)
                room_image_count += 1
            else:
                break
        return image_url_lst
    else:
        return None


def remove_tags(text):  # куда деть эти функции не связанные напрямую с запросами?
    # создать еще один модуль?
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
