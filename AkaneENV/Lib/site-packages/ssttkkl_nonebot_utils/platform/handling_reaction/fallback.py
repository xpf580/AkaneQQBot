import asyncio
from asyncio import sleep, shield, create_task
from contextlib import asynccontextmanager

from nonebot import logger, Bot
from nonebot.internal.adapter import Event


async def send_delayed_loading_prompt(bot: Bot, event: Event):
    try:
        await sleep(5)

        logger.debug(f"send delayed loading")
        await bot.send(event, "努力加载中")
    except asyncio.CancelledError as e:
        raise e
    except BaseException as e:
        logger.exception(e)


@asynccontextmanager
async def handling_reaction(bot: Bot, event: Event):
    task = create_task(send_delayed_loading_prompt(bot, event))

    try:
        yield
    finally:
        if task and not task.done():
            task.cancel()
