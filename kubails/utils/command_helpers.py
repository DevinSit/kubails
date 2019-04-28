from functools import wraps
from typing import Callable


def log_command_args_factory(logger, message: str):
    """Command decorator generator for logging a command's input args."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.debug("%s: {'args': %s, 'kwargs': %s}", message.format(func.__name__), args, kwargs)

            return func(*args, **kwargs)

        return wrapper

    return decorator
