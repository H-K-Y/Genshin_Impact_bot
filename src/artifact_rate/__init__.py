from base64 import b64encode
from io import BytesIO

from .artifact_eval import *


def format_sub_attr(artifact_attr):
    msg = ""
    for i in artifact_attr["sub_item"]:
        msg += f'{i["name"]:\u3000<6} | {i["value"]}\n'
    return msg


async def rate_by_img(image_url: str):
    image_content = BytesIO(requests.get(image_url).content)
    image_b64 = b64encode(image_content.read()).decode()
    artifact_attr = await get_artifact_attr(image_b64)
    rate_result = await rate_artifact(artifact_attr)
    return f'圣遗物评分结果：\n主属性：{artifact_attr["main_item"]["name"]}\n{format_sub_attr(artifact_attr)}' \
           f'------------------------------\n总分：{rate_result["total_percent"]}\n' \
           f'主词条：{rate_result["main_percent"]}\n副词条：{rate_result["sub_percent"]}\n评分、识图均来自genshin.pub'
