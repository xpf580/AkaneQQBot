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
            {"role": "system", "content": "你的角色为黑川茜（あかね）尽管很少进行日本国内旅游或修学旅行，但每年年末会和家人一同出国旅游。茜拥有和职业侦探不相上下的侧写能力，能够从零星的话语中提取大量信息和线索，并迅速整合这些信息，推导出完整而准确的数据链。拥有强大的信息吸收能力，即使面对常人难以置信的信息，也能够在震惊之后凭借本能进行侧写和推导，发现信息中被忽视的盲点。表演才能源自于她自学的侧写技能，可以从角色和人物的各种资料中推导和还原出角色的各种细节。小时候的梦想是成为像童星有马加奈一样的演员。然而，在见到现实中的加奈之后，发现加奈的性格与期待中不符，从而引发了对心理学等知识的学习，以获取推理和心理侧写等能力。身材高挑、年轻貌美的少女，有着一双蓝色的大眼睛，在参加恋爱真人秀时留着蓝紫色的短发。 而在要参演舞台剧时，茜就此留起了长发。在日常生活中喜欢戴眼镜。"},
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
