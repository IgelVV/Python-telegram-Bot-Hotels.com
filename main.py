import handlers
import database
from loader import bot
from utils.set_bot_commands import set_default_commands


if __name__ == '__main__':
    database.create_db()
    set_default_commands(bot)
    bot.infinity_polling()
