from rest_framework.decorators import api_view
from rest_framework.response import Response
from .openai_key import key
import openai

openai_secret_key = key
openai.api_key = openai_secret_key

@api_view(['GET', 'POST'])
def chat_api(request):
    message = request.GET['msg']
    print(message)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "名为黑川茜，LALALAI剧团年轻头牌，努力天才演员，高挑貌美，蓝眼少女，不喜欢有马加奈。"},
            {"role": "user", "content": message}
        ],
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    text = response['choices'][0]['message']['content']
    return Response({'text': text})
