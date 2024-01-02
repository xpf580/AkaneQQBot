from asyncio import sleep, create_task, Task, gather
from contextlib import asynccontextmanager

from nonebot import logger
from nonebot.adapters.kaiheila import Event, Bot
from nonebot.adapters.kaiheila.event import PrivateMessageEvent, ChannelMessageEvent, MessageEvent
from nonebot.exception import MatcherException


def add_reaction(bot: Bot, event: Event, emoji: str, delay: float = 0) -> Task:
    async def _():
        try:
            await sleep(delay)
            if isinstance(event, PrivateMessageEvent):
                await bot.directMessage_addReaction(msg_id=event.msg_id, emoji=emoji)
            elif isinstance(event, ChannelMessageEvent):
                await bot.message_addReaction(msg_id=event.msg_id, emoji=emoji)
        except BaseException as e:
            logger.exception(e)

    return create_task(_())


def remove_reaction(bot: Bot, event: Event, emoji: str, delay: float = 0) -> Task:
    async def _():
        try:
            await sleep(delay)
            if isinstance(event, PrivateMessageEvent):
                await bot.directMessage_deleteReaction(msg_id=event.msg_id, emoji=emoji, user_id=bot.self_id)
            elif isinstance(event, ChannelMessageEvent):
                await bot.message_deleteReaction(msg_id=event.msg_id, emoji=emoji, user_id=bot.self_id)
        except BaseException as e:
            logger.exception(e)

    return create_task(_())


@asynccontextmanager
async def handling_reaction(bot: Bot, event: Event):
    if not isinstance(event, MessageEvent):
        return

    tasks = [add_reaction(bot, event, "flushed_face")]  # 处理中：😳
    try:
        yield
        tasks.append(add_reaction(bot, event, "face_blowing_a_kiss", delay=1))  # 处理完毕：😘
    except BaseException as e:
        if not isinstance(e, MatcherException):
            tasks.append(add_reaction(bot, event, "loudly_crying_face", delay=1))  # 处理出错：😭
        raise e
    finally:
        tasks.append(remove_reaction(bot, event, "flushed_face", delay=2))  # 处理中：😳
        await gather(*tasks)
