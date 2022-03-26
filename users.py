# todo Прочитал о таком способе аннотации методов,
#  выдающих инстанс того же класса. Это допустимо?
from __future__ import annotations


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

    @staticmethod
    def get_user(user_id: int) -> Users:
        """

        :param user_id:
        :return:
        """
        if Users.all_users.get(user_id) is None:
            new_user = Users(user_id)
            return new_user
        return Users.all_users.get(user_id)

    @classmethod
    def add_user(cls, user_id: int, user: Users) -> None:
        """

        :param user_id:
        :param user:
        :return:
        """
        cls.all_users[user_id] = user
