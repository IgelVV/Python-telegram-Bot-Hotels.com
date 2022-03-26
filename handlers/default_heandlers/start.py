from telebot.types import Message

from config_data.config import DEFAULT_COMMANDS
from loader import bot


@bot.message_handler(commands=['start'])
def bot_start(message: Message) -> None:
    """
    Ответ на команду /start

    :param message: Объект сообщения от пользователя
    :return: None
    """
    commands = [f'/{command} - {desk}' for command, desk in DEFAULT_COMMANDS]
    start_massage = 'Это бот для поиска отелей на сайте Hotels.com \n' \
                    'Выберете одну из следующих команд:\n'
    start_massage += '\n'.join(commands)

    bot.send_message(message.chat.id, start_massage)
