from functools import wraps
from typing import Optional, Type, Tuple, Union

from nonebot import get_driver, logger

default_command_start: str = next(iter(get_driver().config.command_start))


def except_log_only_if_trace(t_error: Union[Type[BaseException], Tuple[Type[BaseException]]],
                             msg: Optional[str] = None):
    def deco(func):
        @wraps(func)
        def wrapper(*arg, **kwargs):
            try:
                func(*arg, **kwargs)
            except t_error as e:
                if get_driver().config.log_level == 'TRACE':
                    if msg:
                        logger.opt(exception=e).error(msg)
                    else:
                        logger.exception(e)

        return wrapper

    return deco


__all__ = ("default_command_start",)
