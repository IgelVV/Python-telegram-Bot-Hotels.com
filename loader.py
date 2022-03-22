import os
import telebot
from dotenv import load_dotenv, find_dotenv


# todo Нужно ли выносить класс в отдельный файл?
class Users:
    """
    Класс для хранения информации о пользователе и результатах его поиска
    """

    all_users = dict()

    def __init__(self, user_id: int) -> None:

        self.city = None
        self.found_cities = None
        self.city_id = None
        self.check_in = None
        self.check_out = None
        self.hotels_count = None
        self.command = None
        self.price_range = None
        self.distance = None
        self.with_photos = None
        self.found_hotels = None
        Users.add_user(user_id, self)

# todo как аннотировать этот метод? нельзя указать -> Users
    @staticmethod
    def get_user(user_id: int):
        if Users.all_users.get(user_id) is None:
            new_user = Users(user_id)
            return new_user
        return Users.all_users.get(user_id)

# todo тот же вопрос. кажется что должно быть user: Users
    @classmethod
    def add_user(cls, user_id: int, user) -> None:
        cls.all_users[user_id] = user
# todo нужно ли писать геттеры и сеттеры, если они сейчас не используются?


if not find_dotenv():
    exit('Отсутствует файл .env')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')

bot = telebot.TeleBot(BOT_TOKEN)
