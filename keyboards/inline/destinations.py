from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from logger import logger_wraps, logger


@logger_wraps()
@logger.catch
def destination_request(cities: dict[str, str]) -> InlineKeyboardMarkup:
    """
    Формирует и возвращает Inline клавиатуру, состоящую из названия городов.

    К каждой кнопке прикреплены ID города и тег <city>.
    :param cities: Список городов {ID города: Название}
    :return: Inline клавиатуру
    """
    keyboard = InlineKeyboardMarkup()

    for destination_id in cities.keys():
        callback_data = f'{destination_id}<city>'
        keyboard.add(
            InlineKeyboardButton(text=cities[destination_id],
                                 callback_data=callback_data))
    return keyboard
