from telebot import types
from loader import bot
from database import get_history_requests, get_history_hotels
from users import User
from keyboards.inline.confirmation import confirm_selection
from utils.misc import auxiliary
from logger import logger_wraps, logger


@bot.message_handler(commands=['history'])
@logger_wraps()
@logger.catch
def history_request(message: types.Message, limit: int = 5) -> None:
    """
    Отправляет пользователю несколько прошлых его запросов.

    Обрабатывает команду history.
    Обращается к базе данных за несколькими последними запросами от пользователей,
    присылает их пользователю с инлайн кнопкой.
    :param message: объект сообщения.
    :param limit: количество последних запросов в истории.
    :return: None
    """
    user = User.get_user(message.from_user.id)
    previous_req = get_history_requests(user, limit)
    bot.send_message(message.chat.id, f'Ваши последние {limit} запросов:')
    if len(previous_req):
        for request in previous_req:
            text = (
                f'{request["request_time"]}, {request["command"]},\n'
                f'{request["city_name"]} (показать {request["hotels_count"]}, '
                f'check_in {request["check_in"]}, check_out {request["check_out"]}). '
            )
            if request['command'] == '/bestdeal':
                text = text + f'Цена от {request["price_min"]} до {request["price_max"]}, ' \
                              f'расстояние от центра {request["distance"]}.'
            bot.send_message(message.chat.id, text,
                             reply_markup=confirm_selection(request['request_id'], '<history>'))
    else:
        bot.send_message(message.chat.id, f'История запросов не найдена')


@bot.callback_query_handler(func=lambda call: call.data.endswith("<history>"))
@logger_wraps()
@logger.catch
def callback_history_hotels(call: types.CallbackQuery) -> None:
    """
    Отправляет отели найденные в одном из прошлых запросов.

    Обрабатывает коллбэк от инлайн кнопки под любым из последних запросов,
    полученных от базы данных.
    :param call: callback.
    :return: None
    """
    bot.answer_callback_query(call.id, f"Выбор учтён")

    bot.send_message(call.message.chat.id, f'Выбран запрос:\n{call.message.text}')
    request_id = int(auxiliary.remove_tags(call.data))
    history_hotels = get_history_hotels(request_id)
    text = str()
    if len(history_hotels):
        for hotel in history_hotels:
            hotel_info = (
                f"{hotel['hotel_name']}, "
                f"\nid: {hotel['hotel_id']}, "
                f"расстояние: {hotel['distance_from_center']}, "
                f"\nцена: {hotel['price']}, "
                f"\nадрес: {hotel['address']}"
                f"\nURL: {hotel['hotel_url']}\n\n"
            )
            text += hotel_info
        else:
            bot.send_message(call.message.chat.id, text)
            bot.send_message(call.message.chat.id, f'Было найдено отелей: {len(history_hotels)}')
    else:
        bot.send_message(call.message.chat.id, f'По этому запросу не найдено отелей')
