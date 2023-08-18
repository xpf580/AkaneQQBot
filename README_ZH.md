# AkaneQQBot

**完全升级的 GPTbot，机器人与环境完全分离。贴心地内置了签名服务器。使用 OpenAI 模型 "gpt-3.5-turbo-16k"，添加了提示词：“名为黑川茜，LALALAI 剧团年轻头牌，努力天才演员，高挑貌美，蓝眼少女，不喜欢有马加奈。”还添加了一些基本插件。在 QQ 中使用 `help` 命令查看更多。**

## 使用方法

**可选项**：你可以选择不下载 `./AkaneENV`。在你自己的虚拟环境中，执行以下命令在终端中安装所需的依赖：`pip install -r requirements.txt`

1. 进入 `.\chat\myapp` 目录，在 `openai_key.py` 文件中输入你的 OpenAI API 密钥。

2. 进入 `.\go-cqhttp` 目录，在 `config.yml` 文件中输入你的 QQ 账号密码。

3. 在终端中输入 `.\Akane_quick_start.bat` 或直接运行该脚本。这将打开四个 PowerShell 终端，用于在不同的控制台中调试机器人。