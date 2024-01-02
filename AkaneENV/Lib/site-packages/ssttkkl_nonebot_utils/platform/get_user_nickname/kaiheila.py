from nonebot import get_bot, logger
from nonebot.adapters.kaiheila import Bot
from nonebot_plugin_session import Session, SessionIdType

from .cache import cache
from .fallback import get_user_nickname as fallback


async def get_user_nickname(session: Session) -> str:
    cache_key = session.get_id(SessionIdType.GROUP_USER, include_bot_id=False)

    res = cache.get(cache_key)
    if res is None:
        try:
            bot: Bot = get_bot(session.bot_id)
            view = await bot.user_view(user_id=session.id1, guild_id=session.id3)
            res = view.nickname
        except BaseException as e:
            logger.opt(exception=e).error("获取用户昵称时发生错误")
            res = await fallback(session)

    cache[cache_key] = res
    return res
