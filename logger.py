import functools
import sys
from loguru import logger


def logger_wraps(*, entry=True, exit=False, level="DEBUG"):

    def wrapper(func):
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
