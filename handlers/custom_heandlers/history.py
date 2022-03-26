from telebot.types import Message

from loader import bot


# todo Нужно ли использовать logging?
# todo как использовать базу данных? Хранить в ней найденные отели и введенные пользователем данные?
@bot.message_handler(commands=['history'])
def history_request(message: Message) -> None:
    # Команда /history
    # После ввода команды пользователю выводится история поиска отелей. Сама история
    # содержит:
    # 1. Команду, которую вводил пользователь.
    # 2. Дату и время ввода команды.
    # 3. Отели, которые были найдены.

    bot.send_message(message.chat.id, 'history_request')
