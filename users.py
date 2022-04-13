from __future__ import annotations
from logger import logger_wraps, logger


class User:
    """
    Класс для хранения информации о пользователе и результатах его поиска
    """

    all_users = dict()

    @logger_wraps()
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id
        self.city = None
        self.found_cities = None
        self.city_id = None
        self.check_in = None
        self.check_out = None
        self.hotels_count = None
        self.command = None
        self.price_range = [None, None]
        self.distance = None
        self.with_photos = None
        self.found_hotels = None
        User.add_user(user_id, self)

    @staticmethod
    def get_user(user_id: int) -> User:
        """
        Ищет в поле all_users и возвращает экземпляр класса,
        или создает, сохраняет и возвращает, если не находит.
        :param user_id: id пользователя.
        :return: экземпляр класса.
        """
        if User.all_users.get(user_id) is None:
            new_user = User(user_id)
            return new_user
        return User.all_users.get(user_id)

    @classmethod
    def add_user(cls, user_id: int, user: User) -> None:
        """
        Сохраняет экземпляр класса в поле all_users.
        :param user_id: id пользователя
        :param user:
        :return:
        """
        cls.all_users[user_id] = user
