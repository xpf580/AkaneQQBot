from typing import List

from nonebot import Bot
from nonebot.internal.adapter import Event, Message


async def send_msgs(bot: Bot, event: Event, messages: List[Message]):
    for msg in messages:
        await bot.send(event, msg)
