from functools import wraps
from nonebot.internal.matcher import current_matcher
from nonebot_plugin_saa import MessageFactory, Text
from typing import Optional

from ..errors.error_handler import ErrorHandlers

DEFAULT_ERROR_HANDLERS = ErrorHandlers()


def handle_error(handlers: Optional[ErrorHandlers] = None,
                 silently: bool = False):
    if handlers is None:
        handlers = DEFAULT_ERROR_HANDLERS

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            matcher = current_matcher.get()

            async def receive_error_message(msg: str):
                if not silently:
                    await MessageFactory(Text(msg)).send(reply=True)
                await matcher.finish()

            async with handlers.run_excepting(receive_error_message, reraise_unhandled=True):
                return await func(*args, **kwargs)

        return wrapper

    return decorator
