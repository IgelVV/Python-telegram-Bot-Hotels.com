# дочерний handlers.py, в нем объявляются все кастомные хендлеры - получение города,
# количества отлей и прочее;

import rapidapi
from loader import *
from telegram_bot_calendar import WYearTelegramCalendar, LSTEP
from datetime import date


@bot.message_handler(commands=['start', 'help', 'lowprice', 'highprice', 'bestdeal', 'history'])
def main_request(message):
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
    start_response = '''Это бот для поиска отелей на сайте Hotels.com
    Выберете одну из следующих команд:
    
    /lowprice - поиск самых дешевых отелей
    /highprice - поиск самых дорогих отелей
    /bestdeal - поиск по расширенным параметрам
    /history - история запросов
    /help - список команд
    '''
    bot.send_message(message.chat.id, start_response)
    # история пользователя не сохраняется


def help_request(message):
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
    cities = rapidapi.api_get_locate(message.text)
    # Функция "api_get_locate" уже возвращает список словарей с нужным именем и id
    destinations = types.InlineKeyboardMarkup()
    for city in cities:
        callback_data = f'{city["destination_id"]}<city>'
        destinations.add(
            types.InlineKeyboardButton(text=city['city_name'], callback_data=callback_data))
    bot.send_message(message.from_user.id, 'Уточните, пожалуйста:', reply_markup=destinations)


@bot.callback_query_handler(func=lambda call: call.data.endswith("<city>"))
def callback_query(call):
    user = Users.get_user(call.from_user.id)
    user.city_id = rapidapi.remove_tags(call.data)

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id, "Выбор учтён")

    calendar, step = WYearTelegramCalendar(calendar_id='in',
                                           min_date=date.today(),
                                           locale='ru').build()
    bot.send_message(call.from_user.id, f"Select {LSTEP[step]}", reply_markup=calendar)


@bot.callback_query_handler(func=WYearTelegramCalendar.func(calendar_id='in', ))
def callback_check_in_calendar(call):
    result, key, step = WYearTelegramCalendar(calendar_id='in',
                                              min_date=date.today(),
                                              locale='ru').process(call.data)
    if not result and key:
        bot.edit_message_text(f"Select {LSTEP[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        user = Users.get_user(call.from_user.id)
        user.check_in = result
        bot.edit_message_text(f"You selected {result}",
                              call.message.chat.id,
                              call.message.message_id)

        calendar, step = WYearTelegramCalendar(calendar_id='out', min_date=result,
                                               locale='ru').build()
        bot.send_message(call.from_user.id, f"Select {LSTEP[step]}", reply_markup=calendar)


@bot.callback_query_handler(func=WYearTelegramCalendar.func(calendar_id='out', ))
def callback_check_out_calendar(call):
    user = Users.get_user(call.from_user.id)
    result, key, step = WYearTelegramCalendar(calendar_id='out',
                                              min_date=user.check_in,
                                              locale='ru').process(call.data)
    if not result and key:
        bot.edit_message_text(f"Select {LSTEP[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        user = Users.get_user(call.from_user.id)
        user.check_out = result
        bot.edit_message_text(f"You selected {result}",
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
            bot.register_next_step_handler(message, search_depth)


def price_request(message):
    price_range = rapidapi.price_range_from_text(message.text)
    if len(price_range) == 2:
        user = Users.get_user(message.from_user.id)
        user.price_range = price_range
        bot.send_message(message.chat.id, f'{user.price_range}')
        bot.send_message(message.chat.id, 'Введите расстояние от центра в километрах')
        bot.register_next_step_handler(message, search_radius)
    else:
        bot.send_message(message.chat.id, 'Запишите начальную и конечную цены в формате '
                                          '"500-10000", используйте только цифры')
        bot.register_next_step_handler(message, price_request)


def search_radius(message):
    distance = rapidapi.find_number(message.text)
    if distance:
        user = Users.get_user(message.from_user.id)
        user.distance = distance
        bot.send_message(message.chat.id, user.distance)
        bot.send_message(message.chat.id, 'Введите количество отелей, '
                                          'которые необходимо вывести '
                                          'в результате (не больше 10)')
        bot.register_next_step_handler(message, search_depth)
    else:
        bot.send_message(message.chat.id, 'Введите радиус для поиска отелей в километрах, '
                                          'используйте цифры')
        bot.register_next_step_handler(message, search_radius)


def search_depth(message):
    hotels_count = rapidapi.find_number(message.text)
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
        bot.register_next_step_handler(message, search_depth)


@bot.callback_query_handler(func=lambda call: call.data == 'yes' or call.data == 'no')
def send_photos(call):
    user = Users.get_user(call.from_user.id)
    if call.data == 'yes':
        user.with_photos = True
    else:
        user.with_photos = False

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id, "Выбор учтён")

    found_hotels = rapidapi.api_get_hotels(user)
    count = 0
    for hotel in found_hotels:
        count += 1
        if count <= user.hotels_count:
            bot.send_message(call.message.chat.id,
                             f"{hotel['hotel_name']}, "
                             f"id: {hotel['hotel_id']}, "
                             f"расстояние :{hotel['distance_from_center']}")
        else:
            break


def history_request(message):
    bot.send_message(message.chat.id, 'history_request')
