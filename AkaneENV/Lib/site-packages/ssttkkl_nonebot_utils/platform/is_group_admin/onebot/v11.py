from nonebot import get_bot
from nonebot.adapters.qqguild import Bot
from nonebot_plugin_session import Session, SessionLevel


async def is_group_admin(session: Session) -> bool:
    bot: Bot = get_bot(session.bot_id)

    if session.level != SessionLevel.LEVEL2:
        raise ValueError("cannot check group admin on non-group session")

    member_info = await bot.get_group_member_info(group_id=int(session.id2), user_id=int(session.id1))
    return member_info["role"] != "member"
