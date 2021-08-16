from .artifact_eval import *
from hoshino import Service
import requests

from base64 import b64encode
from io import BytesIO

sv = Service("原神圣遗物评分")


def get_format_sub_item(artifact_attr):
    msg = ""
    for i in artifact_attr["sub_item"]:
        msg += f'{i["name"]:\u3000<6} | {i["value"]}\n'
    return msg


@sv.on_prefix(("圣遗物评分", "-rate"))
async def artifact_rate(bot, ev):
    if '[CQ:image' not in ev["raw_message"]:
        await bot.send(ev, "图呢？\n*请将-rate指令与截图一起发送", at_sender=True)
        return
    if len(ev["message"]) > 1:
        await bot.send(ev, "只能上传一张截图哦", at_sender=True)
        return
    for i in ev["message"]:
        if i["type"] == 'image':
            image_url = i.data["url"]
            break
        continue
    # await bot.send(ev, f"图片收到啦~\n正在识图中...")
    image_content = BytesIO(requests.get(image_url).content)
    image_b64 = b64encode(image_content.read()).decode()
    try:
        artifact_attr = await get_artifact_attr(image_b64)
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        await bot.send(ev, f"连接超时", at_sender=True)
        return
    if 'err' in artifact_attr.keys():
        err_msg = artifact_attr["full"]["message"]
        await bot.send(ev, f"发生了点小错误：\n{err_msg}", at_sender=True)
        return
    # await bot.send(ev, f"识图成功！\n正在评分中...", at_sender=True)
    rate_result = await rate_artifact(artifact_attr)
    if 'err' in rate_result.keys():
        err_msg = rate_result["full"]["message"]
        await bot.send(ev, f"发生了点小错误：\n{err_msg}\n*注：将在下版本加入属性修改", at_sender=True)
        return
    format_result = f'圣遗物评分结果：\n主属性：{artifact_attr["main_item"]["name"]}\n{get_format_sub_item(artifact_attr)}'\
                    f'------------------------------\n总分：{rate_result["total_percent"]}\n'\
                    f'主词条：{rate_result["main_percent"]}\n副词条：{rate_result["sub_percent"]}\n评分、识图均来自genshin.pub'
    await bot.send(ev, format_result, at_sender=True)
