from functools import lru_cache
from typing import Callable, Mapping, Union

from nonebot import logger, Bot


class UnsupportedBotError(RuntimeError):
    ...


class FuncManager:
    def __init__(self, func: Mapping[str, Callable]):
        self._func = func

    def __getattr__(self, item):
        if item in self._func:
            return self._func[item]
        else:
            raise UnsupportedBotError()


def _get_bot_type(bot: Union[str, Bot]):
    if isinstance(bot, Bot):
        bot_type = bot.type
    else:
        bot_type = bot
    return bot_type


class FuncManagerFactory:
    def __init__(self):
        self._registry = []

    def register(self, bot: Union[str, Bot], func_name: str, func: Callable):
        bot_type = _get_bot_type(bot)
        self._registry.append((bot_type, func_name, func))
        logger.debug(f"registered {func_name} for {bot_type}")

    def is_supported(self, bot: Union[str, Bot], func_name: str) -> bool:
        bot_type = _get_bot_type(bot)
        for reg in self._registry:
            if reg[0] == bot_type and reg[1] == func_name:
                return True

        return False

    @lru_cache(maxsize=8)
    def __call__(self, bot: Union[str, Bot]):
        bot_type = _get_bot_type(bot)
        func_mapping = {}
        for type_, name, func in self._registry:
            if bot_type == type_:
                func_mapping[name] = func
        for type_, name, func in self._registry:
            if type_ == "fallback":
                func_mapping.setdefault(name, func)
        return FuncManager(func_mapping)
