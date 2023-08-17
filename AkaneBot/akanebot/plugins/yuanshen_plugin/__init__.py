from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment
import httpx

yuanshen = on_command(
    '原神',
    block=True,
    priority=11
)


@yuanshen.handle()
async def main():
    msg="原神怎么你了"
    await yuanshen.finish(msg)

wenhao = on_command(
    '？',
    block=True,
    priority=11
)

@wenhao.handle()
async def main():
    msg="¿"
    await wenhao.finish(msg)