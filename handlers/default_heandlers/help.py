from telebot.types import Message
from config_data.config import DEFAULT_COMMANDS
from loader import bot
from logger import logger_wraps, logger


@bot.message_handler(commands=['help'])
@logger_wraps()
@logger.catch
def bot_help(message: Message):
    text = [f'/{command} - {desk}' for command, desk in DEFAULT_COMMANDS]
    bot.send_message(message.chat.id, '\n'.join(text))
