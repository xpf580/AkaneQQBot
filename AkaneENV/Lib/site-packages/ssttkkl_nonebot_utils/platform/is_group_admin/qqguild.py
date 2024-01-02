from nonebot import get_bot
from nonebot.adapters.qqguild import Bot
from nonebot_plugin_session import Session, SessionLevel


async def is_group_admin(session: Session) -> bool:
    bot: Bot = get_bot(session.bot_id)

    if session.level != SessionLevel.LEVEL3:
        raise ValueError("cannot check group admin on non-group session")

    perm = await bot.get_channel_permissions(channel_id=session.id2, user_id=session.id1)
    perm = int(perm.permissions, 0)
    return bool(perm & 2)
