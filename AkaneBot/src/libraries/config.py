class Config:
    # 机器人QQ号
    bot_id = '1795852754'
    # Bot的超级管理员
    superuser = ['1286020114']
    # ChatGPT的认证选项（1为使用账号密码，2为使用session_token）
    # 若选择了其中一个，则无需填写其他选项的对应配置
    openai_authentication = 1
    # 1-ChatGPT的账号（邮箱）
    openai_email = 'qq1286020114@outlook.com'
    # 1-ChatGPT的密码
    openai_password = '18947279281pps'
    # ChatGPT使用的代理（请务必修改为自己的代理！请确保该代理可以正常使用chat.openai.com的ChatGPT）
    openai_proxy = 'https://youtulink.top/api/v1/client/subscribe?token=eaff4cdd00ac8ffdd59e99e7d6b5f882'
    # 2-ChatGPT的session_token
    openai_session_token = 'Session Token'