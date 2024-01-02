from nonebot import get_bot, logger
from nonebot.adapters.onebot.v11 import Bot
from nonebot_plugin_session import Session, SessionLevel, SessionIdType

from ..cache import cache
from ..fallback import get_user_nickname as fallback


async def get_user_nickname(session: Session) -> str:
    cache_key = session.get_id(SessionIdType.GROUP_USER, include_bot_id=False)

    res = cache.get(cache_key)
    if res is None:
        try:
            bot: Bot = get_bot(session.bot_id)
            if session.level == SessionLevel.LEVEL2:
                user_info = await bot.get_group_member_info(group_id=int(session.id2), user_id=int(session.id1))
                return user_info["card"] or user_info["nickname"]
            else:
                user_info = await bot.get_stranger_info(user_id=int(session.id1))
                return user_info["nickname"]
        except BaseException as e:
            logger.opt(exception=e).error("获取用户昵称时发生错误")
            res = await fallback(session)

    cache[cache_key] = res
    return res
