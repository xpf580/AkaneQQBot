from nonebot_plugin_session import Session, SessionIdType


async def get_user_nickname(session: Session) -> str:
    return session.get_id(SessionIdType.USER, include_bot_type=False, include_bot_id=False)
