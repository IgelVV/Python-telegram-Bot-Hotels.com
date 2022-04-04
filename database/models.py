from peewee import *
from datetime import datetime
import os.path


db = SqliteDatabase(os.path.join('database', 'bot_history.db'))


class BaseModel(Model):
    """
    Базовая модель для наследования
    """
    class Meta:
        """
        Метакласс для настройки таблиц базы данных
        """
        database = db


class Request(BaseModel):
    """
    Класс описывающий таблицу requests.
    """
    request_id = AutoField()
    request_time = DateTimeField(default=datetime.now())
    user_id = IntegerField()
    command = CharField()
    city_id = CharField()
    city_name = CharField()
    check_in = DateField()
    check_out = DateField()
    hotels_count = IntegerField()
    price_min = IntegerField(null=True)
    price_max = IntegerField(null=True)
    distance = IntegerField(null=True)
    with_photos = BooleanField()

    class Meta:
        """
        Расширение мета класса
        """
        db_table = 'requests'


class Hotel(BaseModel):
    """
    Класс описывающий таблицу hotels.
    """
    hotel_id = CharField()
    hotel_name = CharField()
    distance_from_center = CharField()
    price = CharField()
    address = CharField()
    hotel_url = CharField()
    request = ForeignKeyField(Request, backref='found_hotels')

    class Meta:
        """
        Расширение мета класса
        """
        db_table = 'hotels'
