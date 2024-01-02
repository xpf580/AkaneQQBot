import requests
import nonebot
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter  # 避免重复命名
from collections import defaultdict

# 初始化 NoneBot
nonebot.init()


# 注册适配器
app = nonebot.get_asgi()
driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)


# 在这里加载插件
nonebot.load_builtin_plugins("echo")  # 内置插件
# nonebot.load_from_toml("pyproject.toml") 
# nonebot.load_plugin("thirdparty_plugin")  # 第三方插件
nonebot.load_plugins("AkaneBot/plugins")  # 本地插件
nonebot.load_plugin('nonebot_plugin_osubot')
nonebot.load_plugin('nonebot_plugin_simplemusic')



if __name__ == "__main__":
    nonebot.run()