import functools
import logging
from typing import Union


class DefaultLogger:
    def __init__(self):
        pass

    def get_logger(self):
        return logging.getLogger('reportassistant.default')

def get_default_logger():
    return DefaultLogger().get_logger()

def log(_func=None, *, my_logger: Union[DefaultLogger, logging.Logger] = None):
    def decorator_log(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if my_logger is None:
                logger = get_default_logger()
            else:
                if isinstance(my_logger, DefaultLogger):
                    logger = my_logger.get_logger()
                else:
                    logger = my_logger
            args_repr = [repr(a) for a in args]
            kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            logger.debug(f"function {func.__name__} called with args {signature}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"function {func.__name__} return with {result if result else 'No result'}")
                return result
            except Exception as e:
                logger.exception(f"Exception raised in {func.__name__}. exception: {str(e)}")
                raise e
        return wrapper

    if _func is None:
        return decorator_log
    else:
        return decorator_log(_func)