from PIL import Image,ImageDraw,ImageFont
from io import BytesIO

import os
import json
import random
import base64
import time


FILE_PATH = os.path.dirname(__file__)
FONT_PATH = os.path.join(FILE_PATH,"汉仪文黑.ttf")

data = {} # config.json里的数据

almanac_data = {
    # 生成的黄历base64字符串和黄历更新日期
    "date" : "",
    "almanac_base64_str" :""
}


chinese = {"0":"","1":"一","2":"二","3":"三","4":"四","5":"五","6":"六","7":"七","8":"八","9":"九"}

def month_to_chinese(month:str):
    # 把日期数字转成中文数字
    m = int(month)
    if m < 10 :
        return chinese[month[-1]]
    elif m < 20 :
        return "十" + chinese[month[-1]]
    else:
        return chinese[month[0]] + "十" + chinese[month[-1]]


def load_data():
    # 载入config.json文件的数据
    global data
    with open(os.path.join(FILE_PATH, 'config.json'), 'r', encoding='UTF-8') as f:
        data = json.load(f)

    almanac_data["date"] = ""
    almanac_data["almanac_base64_str"] = ""


def seed_random_list(seed:str,l:list):
    # 使用随机种子随机选择列表中的元素，相同的种子和列表将返回同样的输出
    seed = seed + str(l)
    random.seed(seed)
    index = random.random() * len(l)
    print(f"index : {index}")

    return l[int(index)]



def generate_almanac():
    # 生成黄历图片，然后转换成base64保存到 almanac_data["almanac_base64_str"]

    seed = time.strftime("%Y-%m-%d")
    offset = 1
    today_luck = []
    l = list(data.keys())

    while len(today_luck) < 6:
        # 随机6个不同的运势放到 today_luck
        r = seed_random_list(str(offset) + seed , l)
        if r in today_luck:
            offset += 1
        else:
            today_luck.append(r)

    back = Image.open(os.path.join(FILE_PATH, "back.png"))

    year = time.strftime("%Y")
    month = month_to_chinese(time.strftime("%m")) + "月"
    day = month_to_chinese(time.strftime("%d")) + "日"

    draw = ImageDraw.Draw(back)
    draw.text((88, 122), year, fill="#8d7650ff", font=ImageFont.truetype(FONT_PATH, size=25), anchor="mm",align="center")
    draw.text((200, 122), day, fill="#f7f8f2ff", font=ImageFont.truetype(FONT_PATH, size=27), anchor="mm",align="center")
    draw.text((305, 122), month, fill="#8d7650ff", font=ImageFont.truetype(FONT_PATH, size=25), anchor="mm",align="center")

    buff = Image.new("RGBA", (250, 125))
    debuff = Image.new("RGBA", (250, 125))

    buff_draw = ImageDraw.Draw(buff)
    debuff_draw = ImageDraw.Draw(debuff)

    for i in range(3):
        buff_name = today_luck[i]
        debuff_name = today_luck[(i+3)]

        buff_effect = seed_random_list(seed , data[buff_name]["buff"] )
        debuff_effect = seed_random_list(seed , data[buff_name]["debuff"] )

        buff_draw.text((0, i * 40), buff_name, fill="#756141ff", font=ImageFont.truetype(FONT_PATH, size=15))
        debuff_draw.text((0, i * 40), debuff_name, fill="#756141ff", font=ImageFont.truetype(FONT_PATH, size=15))

        buff_draw.text((0, i * 40 + 20), buff_effect, fill="#b5b3acff", font=ImageFont.truetype(FONT_PATH, size=11))
        debuff_draw.text((0, i * 40 + 20), debuff_effect, fill="#b5b3acff", font=ImageFont.truetype(FONT_PATH, size=11))

    back.paste(buff, (110, 175), buff)
    back.paste(buff, (110, 300), debuff)

    bio = BytesIO()
    back.save(bio, format='PNG')
    base64_str = base64.b64encode(bio.getvalue()).decode()

    almanac_data["date"] = time.strftime("%Y-%m-%d")
    almanac_data["almanac_base64_str"] = 'base64://' + base64_str


def get_almanac_base64_str():

    if almanac_data["date"] == time.strftime("%Y-%m-%d"):
        return almanac_data["almanac_base64_str"]
    else:
        generate_almanac()
        return almanac_data["almanac_base64_str"]

