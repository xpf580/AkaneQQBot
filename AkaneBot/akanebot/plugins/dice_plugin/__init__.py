from nonebot import on_command, on_regex
from nonebot.params import CommandArg, EventMessage
from nonebot.adapters import Bot, Event, Message
from nonebot.adapters.onebot.v11 import Message, MessageSegment
import random
import re

rxdice = on_regex(r"^r[0-9]+d[0-9]+")

dice = on_command(
    'dice',
    aliases={"d", "D"},
    priority=11
)

@rxdice.handle()
async def handle_rxdice(bot: Bot, event: Event):
    user = event.get_user_id()
    at_ = f"[CQ:at,qq={user}]"
    result_messages = []

    plaintext = event.get_plaintext()
    match = re.match(r"^r([0-9]+)d([0-9]+)", plaintext)
    if match:
        round_num = int(match.group(1))  # 捕获1
        if round_num > 8:
            await rxdice.finish('round_num 值必须小于 8')
            return  # 返回以终止函数继续执行

        dice_num = int(match.group(2))  # 捕获2
        if dice_num > 100000:
            await rxdice.finish('dice_num 值必须小于 100000')
            return  # 返回以终止函数继续执行

        for _ in range(round_num):
            random_value = random.random() * dice_num
            random_value = int(random_value)
        
            if random_value > 0.95 * dice_num:
                result = f'd {dice_num} 的结果是 {random_value} ，大失败!!'
            elif random_value > 0.5 * dice_num:
                result = f'd {dice_num} 的结果是 {random_value} ，失败!'
            elif random_value > 0.05 * dice_num:
                result = f'd {dice_num} 的结果是 {random_value} ，成功!'
            else:
                result = f'd {dice_num} 的结果是 {random_value} ，大成功!!'
            
            result_messages.append(result)
    
        msg = "\n".join(result_messages)
        rxdice_msg = f'{at_}\n{msg}'
        await rxdice.finish(message=Message(rxdice_msg))


@dice.handle()
async def roll_dice(bot: Bot, event: Event):
    input_text = event.get_plaintext().lstrip('dD')
    times = 1

    if input_text.startswith('r'):
        input_text = input_text.lstrip('rR')
        if input_text.isdigit():
            times = int(input_text)
    
    if not input_text.isdigit():
        await bot.send(event, '请输入有效的正整数！')
        return

    dice_value = int(input_text)

    if dice_value <= 0:
        await bot.send(event, '骰子面数必须是正整数！')
        return
    
    user = event.get_user_id()
    at_ = f"[CQ:at,qq={user}]"

    result_messages = []

    for _ in range(times):
        random_value = random.random() * dice_value
        random_value = int(random_value)

        if random_value > 0.8 * dice_value:
            result = f'd {dice_value} 的结果是 {random_value} ，大成功！'
        elif random_value > 0.5 * dice_value:
            result = f'd {dice_value} 的结果是 {random_value} ，成功'
        elif random_value > 0.2 * dice_value:
            result = f'd {dice_value} 的结果是 {random_value} ，失败'
        else:
            result = f'd {dice_value} 的结果是 {random_value} ，大失败!'
        
        result_messages.append(at_ + result)

    msg = "\n".join(result_messages)
    await dice.finish(message=Message(msg))