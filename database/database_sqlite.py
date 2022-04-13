from .models import db, Request, Hotel
from users import User
from logger import logger_wraps, logger


@logger_wraps()
@logger.catch
def create_db() -> None:
    """
    Создает базу данных, если ее нет.
    :return: None
    """
    with db:
        db.create_tables([Request, Hotel])


@logger_wraps()
@logger.catch
def save_history(user: User) -> None:
    """
    Сохраняет данные пользователя в базу данных
    :param user: Экземпляр класса User
    :return: None
    """

    with db:
        request = Request.create(
            user_id=user.user_id,
            command=user.command,
            city_id=user.city_id,
            city_name=user.city,
            check_in=user.check_in,
            check_out=user.check_out,
            hotels_count=user.hotels_count,
            price_min=user.price_range[0],
            price_max=user.price_range[1],
            distance=user.distance,
            with_photos=user.with_photos
        )
        data = list()
        for hotel in user.found_hotels:
            hotel_data = {
                'hotel_id': hotel['hotel_id'],
                'hotel_name': hotel['hotel_name'],
                'distance_from_center': hotel['distance_from_center'],
                'price': hotel['price'],
                'address': hotel['address'],
                'hotel_url': hotel['url'],
                'request': request
            }
            data.append(hotel_data)
        Hotel.insert_many(data).execute()


@logger_wraps()
@logger.catch
def get_history_requests(user: User, limit=int) -> list[dict[str: str]]:
    """
    Получает данные нескольких последних запросов пользователя из базы данных.
    :param user: Экземпляр класса User.
    :param limit: количество последних запросов.
    :return: Список словарей с данными запросов.
    """

    result = list()
    with db:
        history_requests = Request.select(
            Request.request_id,
            Request.user_id,
            Request.request_time,
            Request.command,
            Request.city_name,
            Request.check_in,
            Request.check_out,
            Request.hotels_count,
            Request.price_min,
            Request.price_max,
            Request.distance
        ).where(Request.user_id == user.user_id).order_by(Request.request_time.desc()).limit(limit)

        for request in history_requests:
            request_params = {
                'request_id': request.request_id,
                'request_time': request.request_time,
                'command': request.command,
                'city_name': request.city_name,
                'hotels_count': request.hotels_count,
                'check_in': request.check_in,
                'check_out': request.check_out
            }
            if request.command == '/bestdeal':
                request_params['price_min'] = request.price_min
                request_params['price_max'] = request.price_max
                request_params['distance'] = request.distance
            result.append(request_params)
    return result


@logger_wraps()
@logger.catch
def get_history_hotels(request_id: int) -> list[dict[str: str]]:
    """
    Получает данные отелей, найденных ранее из базы данных.

    :param request_id: ID запроса, которым были найдены отели.
    :return: Список словарей с данными отелей.
    """
    result = list()
    with db:
        hotels = Hotel.select().where(Hotel.request == request_id)

        for hotel in hotels:
            hotel_data = {
                'hotel_id': hotel.hotel_id,
                'hotel_name': hotel.hotel_name,
                'hotel_url': hotel.hotel_url,
                'distance_from_center': hotel.distance_from_center,
                'price': hotel.price,
                'address': hotel.address
            }
            result.append(hotel_data)
        return result
