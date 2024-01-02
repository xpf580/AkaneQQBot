from nonebot import on_command
import requests
from nonebot.adapters.onebot.v11 import MessageSegment

setu = on_command("setu", aliases={'色图','涩图'},block=True, priority=11)

@setu.handle()
async def setu_handler():
    img_url = "" 
    url = "https://api.lolicon.app/setu/v2"
    params = {
        "num": 1,
        "r18": 0,
        "excludeAI": True,
        #"tag": ["萝莉|少女", "白丝|黑丝"],
        
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        setu_data = data.get("data", [])[0]  
        pid = setu_data.get("pid")
        title = setu_data.get("title")
        author = setu_data.get("author")
        img_url = setu_data.get("urls")
        url = img_url.get('original', '')
    
        message = f"PID: {pid}\nTitle: {title}\nAuthor: {author}"
    else:
        message = f"Error: {response.status_code}"

    await setu.finish(message + MessageSegment.image(url))
