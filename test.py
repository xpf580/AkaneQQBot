import random
import re

dice_value = 80

times = 3  # 进行投掷的次数
for _ in range(times):
    # 生成一个随机的骰子点数，乘以dice_value确保在骰子面数范围内
    random_value = random.random() * dice_value
    random_value = int(random_value)  # 取整，得到最终点数

    if random_value > 0.8 * dice_value:
        result = f'd {dice_value} 的结果是 {random_value} ，大成功！'
    elif random_value > 0.5 * dice_value:
        result = f'd {dice_value} 的结果是 {random_value} ，成功'
    elif random_value > 0.2 * dice_value:
        result = f'd {dice_value} 的结果是 {random_value} ，失败'
    else:
        result = f'd {dice_value} 的结果是 {random_value} ，大失败!'

    print(result)