from functools import wraps

from nonebot.internal.matcher import current_bot, current_event

from ..platform import platform_func


def with_handling_reaction():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                bot = current_bot.get()
                event = current_event.get()
            except LookupError:
                await func(*args, **kwargs)
                return

            async with platform_func(bot.type).handling_reaction(bot, event):
                await func(*args, **kwargs)

        return wrapper

    return decorator
