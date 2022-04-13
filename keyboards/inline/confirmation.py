from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from logger import logger_wraps, logger


@logger_wraps()
@logger.catch
def confirm_selection(data: str, tag: str) -> InlineKeyboardMarkup:
    """
    Формирует и возвращает Inline клавиатуру, состоящую одной кнопки "Выбрать".

    К кнопке прикреплены данные коллбэка и тег в формате <tag>.
    :param tag: тег в формате <tag>.
    :param data: данные коллбэка.
    :return: Inline клавиатуру.
    """
    keyboard = InlineKeyboardMarkup()
    callback_data = str(data) + tag
    keyboard.add(
        InlineKeyboardButton(text="Выбрать",
                             callback_data=callback_data))

    return keyboard
