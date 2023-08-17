from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment
import httpx
import random

help = on_command(
    'help',
    block=True,
    priority=11
)


@help.handle()
async def main():
    msg="丁真：发送一张丁真照片\njk:发送一张JK照片\n网易云热评：随机网易云热评\n输入GPT/gpt/ai/AI + 需要查询的内容:调用gpt3\n\nAkaneBot by xpf580\n"
    msg+="random"+str(random.randint(10000, 99999))
    await help.finish(msg)
