import peewee
from datetime import datetime
import os.path


db = peewee.SqliteDatabase(os.path.join('database', 'bot_history.db'))


class BaseModel(peewee.Model):
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
    request_id = peewee.AutoField()
    request_time = peewee.DateTimeField(default=datetime.now())
    user_id = peewee.IntegerField()
    command = peewee.CharField()
    city_id = peewee.CharField()
    city_name = peewee.CharField()
    check_in = peewee.DateField()
    check_out = peewee.DateField()
    hotels_count = peewee.IntegerField()
    price_min = peewee.IntegerField(null=True)
    price_max = peewee.IntegerField(null=True)
    distance = peewee.IntegerField(null=True)
    with_photos = peewee.BooleanField()

    class Meta:
        """
        Расширение мета класса
        """
        db_table = 'requests'


class Hotel(BaseModel):
    """
    Класс описывающий таблицу hotels.
    """
    hotel_id = peewee.CharField()
    hotel_name = peewee.CharField()
    distance_from_center = peewee.CharField()
    price = peewee.CharField()
    address = peewee.CharField()
    hotel_url = peewee.CharField()
    request = peewee.ForeignKeyField(Request, backref='found_hotels')

    class Meta:
        """
        Расширение мета класса
        """
        db_table = 'hotels'
