import functools
import sys
from loguru import logger
from typing import Callable


def logger_wraps(*, entry: bool = True, exit: bool = False, level: str = "DEBUG") -> Callable:
    """
    Декоратор для логирования запуска и завершения функции.

    :param entry: логирование при старте.
    :param exit: логирование при завершении.
    :param level: уровень логирования.
    :return: оберточная функция.
    """

    def wrapper(func: Callable) -> Callable:
        name = func.__name__

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            logger_ = logger.opt(depth=1)
            if entry:
                logger_.log(level, "Entering '{}' (args={}, kwargs={})", name, args, kwargs)
            result = func(*args, **kwargs)
            if exit:
                logger_.log(level, "Exiting '{}' (result={})", name, result)
            return result

        return wrapped

    return wrapper


logger.configure(handlers=[
        dict(sink=sys.stderr, diagnose=False)])

logger.add('bot_info.log', level='INFO', diagnose=False, rotation='10MB', retention=3)
