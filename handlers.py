import rapidapi
import auxiliary
from loader import *
from telegram_bot_calendar import WYearTelegramCalendar
from datetime import date
from requests import RequestException
from telebot.apihelper import ApiTelegramException


@bot.message_handler(commands=['start', 'help', 'lowprice', 'highprice', 'bestdeal', 'history'])
def main_request(message):
    """
    Запускает цепочку хэндлеров, реагирует на команды

    :param message:
    :return:
    """
    user = Users.get_user(message.from_user.id)
    user.command = message.text

    if message.text == '/start':
        start_request(message)
    elif message.text == '/help':
        help_request(message)
    elif message.text == '/history':
        history_request(message)
    else:
        bot.send_message(message.chat.id, 'Введите название города')
        bot.register_next_step_handler(message, city_request)


def start_request(message):
    """
    Ответ на команду /start

    :param message:
    :return:
    """
    start_response = '''Это бот для поиска отелей на сайте Hotels.com
    Выберете одну из следующих команд:
    
    /lowprice - поиск самых дешевых отелей
    /highprice - поиск самых дорогих отелей
    /bestdeal - поиск по расширенным параметрам
    /history - история запросов
    /help - список команд
    '''
    bot.send_message(message.chat.id, start_response)


def help_request(message):
    """
    Ответ на команду /help

    :param message:
    :return:
    """
    help_response = '''
    Список доступных команд:
    
    /lowprice - поиск самых дешевых отелей
    /highprice - поиск самых дорогих отелей
    /bestdeal - поиск отелей в диапазоне цен
    /history - история запросов
    /help - список команд
    '''
    bot.send_message(message.chat.id, help_response)


def city_request(message):
    """
    Находит на сайте Hotels.com города по запросу и выводит в inline клавиатуру для уточнения.
    Вызывается при отправке в бот одной из команд для поиска отелей.

    :param message:
    :return:
    """

    user = Users.get_user(message.from_user.id)
    try:
        cities = rapidapi.api_get_locate(message.text)
    except (RequestException, KeyError, TypeError) as ex:
        print(f'{type(ex).__name__}: {ex}')
        bot.send_message(message.chat.id, f'При обращении к сайту Hotels произошла ошибка')
        return None

    destinations = types.InlineKeyboardMarkup()

    user.found_cities = cities
    if len(cities):
        for destination_id in cities.keys():
            callback_data = f'{destination_id}<city>'
            destinations.add(
                types.InlineKeyboardButton(text=cities[destination_id],
                                           callback_data=callback_data))
        bot.send_message(message.from_user.id, 'Уточните, пожалуйста:',
                         reply_markup=destinations)
    else:
        bot.send_message(message.chat.id, f'По запросу "{message.text}" ничего не найдено.')


@bot.callback_query_handler(func=lambda call: call.data.endswith("<city>"))
def callback_query_city(call):
    """
    Сохраняет выбор города после уточнения.
    Выводит inline календарь для выбора даты заезда.

    :param call:
    :return:
    """
    user = Users.get_user(call.from_user.id)
    user.city_id = auxiliary.remove_tags(call.data)

    bot.answer_callback_query(call.id, f"Выбор учтён")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.from_user.id, f"{user.found_cities[user.city_id]}")

    calendar, step = WYearTelegramCalendar(calendar_id='in',
                                           min_date=date.today(),
                                           locale='ru').build()
    bot.send_message(call.from_user.id, "Выберите дату заезда", reply_markup=calendar)


@bot.callback_query_handler(func=WYearTelegramCalendar.func(calendar_id='in'))
def callback_check_in_calendar(call):
    """
    Сохраняет выбор даты заезда
    Выводит inline календарь для выбора даты отъезда.

    :param call:
    :return:
    """
    result, key, step = WYearTelegramCalendar(calendar_id='in',
                                              min_date=date.today(),
                                              locale='ru').process(call.data)
    if not result and key:
        bot.edit_message_text(f"Выберите дату заезда",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        user = Users.get_user(call.from_user.id)
        user.check_in = result
        bot.edit_message_text(f"Вы выбрали {result}",
                              call.message.chat.id,
                              call.message.message_id)

        calendar, step = WYearTelegramCalendar(calendar_id='out', min_date=result,
                                               locale='ru').build()
        bot.send_message(call.from_user.id, "Выберите дату отъезда", reply_markup=calendar)


@bot.callback_query_handler(func=WYearTelegramCalendar.func(calendar_id='out'))
def callback_check_out_calendar(call):
    """
    Сохраняет выбор даты отъезда
    Если выбрана команда /bestdeal, то запрашивает диапазон цен.
    Если выбрана команды /lowprice или /highprice, то сразу запрашивает количество отелей

    :param call:
    :return:
    """
    user = Users.get_user(call.from_user.id)
    result, key, step = WYearTelegramCalendar(calendar_id='out',
                                              min_date=user.check_in,
                                              locale='ru').process(call.data)
    if not result and key:
        bot.edit_message_text(f"Выберите дату отъезда",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        user = Users.get_user(call.from_user.id)
        user.check_out = result
        bot.edit_message_text(f"Вы выбрали {result}",
                              call.message.chat.id,
                              call.message.message_id)

        if user.command == '/bestdeal':
            message = bot.send_message(call.from_user.id,
                                       'Введите диапазон цен (например: 1000-5000)')
            bot.register_next_step_handler(message, price_request)
        else:
            message = bot.send_message(call.from_user.id, 'Введите количество отелей, '
                                                          'которые необходимо вывести '
                                                          'в результате (не больше 10)')
            bot.register_next_step_handler(message, search_depth_request)


def price_request(message):
    """
    Сохраняет диапазон цен
    Запрашивает расстояние до центра

    :param message:
    :return:
    """
    price_range = auxiliary.price_range_from_text(message.text)
    if len(price_range) == 2:
        user = Users.get_user(message.from_user.id)
        user.price_range = price_range
        bot.send_message(message.chat.id, f'{user.price_range}')
        bot.send_message(message.chat.id, 'Введите расстояние от центра в километрах')
        bot.register_next_step_handler(message, search_radius_request)
    else:
        bot.send_message(message.chat.id, 'Запишите начальную и конечную цены в формате '
                                          '"500-10000", используйте только цифры')
        bot.register_next_step_handler(message, price_request)


def search_radius_request(message):
    """
    Сохраняет расстояние до центра
    Запрашивает количество отелей
    :param message:
    :return:
    """
    distance = auxiliary.find_number(message.text)
    if distance is not None:
        user = Users.get_user(message.from_user.id)
        user.distance = distance
        bot.send_message(message.chat.id, user.distance)
        bot.send_message(message.chat.id, 'Введите количество отелей, '
                                          'которые необходимо вывести '
                                          'в результате (не больше 10)')
        bot.register_next_step_handler(message, search_depth_request)
    else:
        bot.send_message(message.chat.id, 'Введите радиус для поиска отелей в километрах, '
                                          'используйте цифры')
        bot.register_next_step_handler(message, search_radius_request)


def search_depth_request(message):
    """
    Сохраняет количество отелей.
    Запрашивает у пользователя выводить ли фотографии отелей.
    :param message:
    :return:
    """
    hotels_count = auxiliary.find_number(message.text)
    if hotels_count is not None and 1 <= hotels_count <= 10:
        user = Users.get_user(message.from_user.id)
        user.hotels_count = hotels_count

        yes_no_question = types.InlineKeyboardMarkup()
        yes_no_question.add(types.InlineKeyboardButton(text='Да', callback_data='yes'))
        yes_no_question.add(types.InlineKeyboardButton(text='Нет', callback_data='no'))
        bot.send_message(message.from_user.id,
                         'Показать фотографии отелей?',
                         reply_markup=yes_no_question)
    else:
        bot.send_message(message.chat.id, 'Введите число от 1 до 10')
        bot.register_next_step_handler(message, search_depth_request)


@bot.callback_query_handler(func=lambda call: call.data == 'yes' or call.data == 'no')
def callback_send_photos(call):
    """
    Сохраняет требуются ли фотографии.
    Запускает функцию поиска отелей.
    :param call:
    :return:
    """
    user = Users.get_user(call.from_user.id)
    if call.data == 'yes':
        user.with_photos = True
    else:
        user.with_photos = False

    bot.answer_callback_query(call.id, "Выбор учтён")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, 'Ведется поиск отелей...')
    send_result(call.message)


def send_result(message):
    """
    Обращается к API Hotels, получает данные подходящих по запросу отелей и выводит пользователю.
    :param message:
    :return:
    """
    user = Users.get_user(message.chat.id)
    try:
        found_hotels = rapidapi.api_get_hotels(user)
    except (RequestException, KeyError, TypeError) as ex:
        print(f'{type(ex).__name__}: {ex}')
        bot.send_message(message.chat.id, f'При обращении к сайту Hotels произошла ошибка')
        return None
    user.found_hotels = list()

    count = 0
    for hotel in found_hotels:

        if count < user.hotels_count:
            distance = auxiliary.find_number(hotel['distance_from_center'])
            if user.command == r'/bestdeal':
                if distance is not None:
                    if distance > user.distance:
                        continue
                else:
                    continue

            user.found_hotels.append(hotel)
            hotel_info = (
                f"{hotel['hotel_name']}, "
                f"id: {hotel['hotel_id']}, "
                f"расстояние: {hotel['distance_from_center']}, "
                f"цена: {hotel['price']}, "
                f"URL: https://ru.hotels.com/ho{hotel['hotel_id']}"
            )

            if user.with_photos:
                try:
                    send_hotel_info_with_photos(hotel['hotel_id'], message, hotel_info)
                except (RequestException, KeyError, TypeError) as ex:
                    print(f'{type(ex).__name__}: {ex}')
                    bot.send_message(message.chat.id,
                                     f'При обращении к сайту Hotels произошла ошибка')
                    count -= 1
                except ApiTelegramException as ex:
                    print(f'{type(ex).__name__}: {ex}')
                    try:
                        send_hotel_photos_one_by_one(hotel['hotel_id'], message, hotel_info)
                    except (RequestException, KeyError, TypeError) as ex:
                        print(f'{type(ex).__name__}: {ex}')
                        bot.send_message(message.chat.id,
                                         f'При обращении к сайту Hotels произошла ошибка')
                        count -= 1
            else:
                bot.send_message(message.chat.id, hotel_info)
            count += 1

        else:
            break
    bot.send_message(message.chat.id, f'Поиск завершён, найдено отелей: {count}')


def send_hotel_info_with_photos(hotel_id, message, caption):
    """
    Формирует медиагруппу из фотографий и подписи, и отправляет пользователю
    :param hotel_id:
    :param message:
    :param caption:
    :return:
    """
    photos_url = rapidapi.api_get_photos(hotel_id)

    caption_flag = True
    photos = []
    for single_photo_url in photos_url:
        if caption_flag:
            photos.append(types.InputMediaPhoto(single_photo_url, caption=caption))
            caption_flag = False
        else:
            photos.append(types.InputMediaPhoto(single_photo_url))
    bot.send_media_group(message.chat.id, photos)


def send_hotel_photos_one_by_one(hotel_id, message, caption):
    """
    Для отправки фотографий поштучно, а не медиагруппой в случае ошибки.
    :param hotel_id:
    :param message:
    :param caption:
    :return:
    """
    photos_url = rapidapi.api_get_photos(hotel_id)
    for single_photo_url in photos_url:
        try:
            bot.send_photo(message.chat.id, single_photo_url)
        except ApiTelegramException as ex:
            print(f'{type(ex).__name__}: {ex}')
    bot.send_message(message.chat.id, caption)


def history_request(message):
    # Команда /history
    # После ввода команды пользователю выводится история поиска отелей. Сама история
    # содержит:
    # 1. Команду, которую вводил пользователь.
    # 2. Дату и время ввода команды.
    # 3. Отели, которые были найдены.

    bot.send_message(message.chat.id, 'history_request')
