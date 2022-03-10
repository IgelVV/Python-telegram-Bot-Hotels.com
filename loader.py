import os
import telebot
from telebot import types
from dotenv import load_dotenv


class Users:  # todo сохранять информацию о поиске

    """
    первая строка

    более длинное описание
    """

    all_users = dict()

    def __init__(self, user_id):
        """

        :param user_id:
        """
        self.city = None
        self.city_id = None  # todo сделать сеттер с проверкой int
        self.check_in = None
        self.check_out = None
        self.hotels_count = None
        self.command = None
        self.price_range = None
        self.distance = None
        self.with_photos = None
        self.found_hotels = None
        Users.add_user(user_id, self)

    @staticmethod
    def get_user(user_id):
        if Users.all_users.get(user_id) is None:
            new_user = Users(user_id)
            return new_user
        return Users.all_users.get(user_id)

    @classmethod
    def add_user(cls, user_id, user):
        cls.all_users[user_id] = user


load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')

bot = telebot.TeleBot(BOT_TOKEN)
