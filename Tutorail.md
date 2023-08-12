## 使用 NoneBot 框架搭建的机器人具有以下几个基本组成部分：

NoneBot 机器人框架主体：负责`连接各个组成部分`，提供基本的机器人功能

驱动器 Driver：客户端/服务端的功能实现，负责接收和发送消息（通常为 HTTP 通信）

适配器 Adapter：驱动器的上层，负责将平台消息与 NoneBot 事件/操作系统的消息格式相互转换

插件 Plugin：机器人的功能实现，通常为负责处理事件并进行一系列的操作

## 请在你的项目目录下执行该命令。nb-cli 会自动安装插件并将其添加到加载列表中。(以下plugin可替换为adapter、driver)

# 列出商店所有插件
nb plugin list

# 搜索商店插件
nb plugin search [可选关键词]

# 升级和卸载插件可以使用以下命令
nb plugin update <插件名称>
nb plugin uninstall <插件名称>

