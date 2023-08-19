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
    msg='''今日舞萌 查看今天的舞萌运势
XXXmaimaiXXX什么 随机一首歌
随个[dx/标准][绿黄红紫白]<难度> 随机一首指定条件的乐曲
查歌<乐曲标题的一部分> 查询符合条件的乐曲
[绿黄红紫白]id<歌曲编号> 查询乐曲信息或谱面信息
<歌曲别名>是什么歌 查询乐曲别名对应的乐曲
定数查歌 <定数>  查询定数对应的乐曲
定数查歌 <定数下限> <定数上限>
分数线 <难度+歌曲id> <分数线> 详情请输入“分数线 帮助”查看
@bot+输入GPT/gpt/ai/AI + 内容:用gpt-3.5-turbo-16k回答
丁真 随机丁真照片 jk:随机JK照片 网易云热评：随机网易云热评
    AkaneBot by xpf580
    '''
    msg+="random"+str(random.randint(10000, 99999))
    await help.finish(msg)

