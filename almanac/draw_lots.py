from PIL import Image, ImageDraw, ImageFont
from .almanac import month_to_chinese
from .tweaks import text_r90
import textwrap
import random
import time
import json
import os

FILE_PATH = os.path.dirname(__file__)
FONT_PATH = os.path.join(FILE_PATH, "assets", "汉仪文黑.ttf")
LIST_PATH = os.path.join(FILE_PATH, "assets", "lots_list.json")
BG_PATH = os.path.join(FILE_PATH, "assets", "lots_bg.png")

with open(LIST_PATH, "r", encoding="UTF-8") as f:
    lots_list = json.loads(f.read())
    lots_items = list(lots_list.keys())


time_font = ImageFont.truetype(FONT_PATH, 30)
lot_font = ImageFont.truetype(FONT_PATH, 25)
question_x = 250
question_y = 300


def make_draw():
    return random.choice(lots_items)


def draw_info(pos):
    draw_result = dict({"pos": pos}, **lots_list[pos])
    return draw_result


def gen_pic(result):
    bg = Image.open(BG_PATH)
    pen = ImageDraw.Draw(bg)

    # 文本
    year = time.strftime("%Y")
    month = month_to_chinese(time.strftime("%m")) + "月"
    day = month_to_chinese(time.strftime("%d"))
    # 正文
    final_lots = result
    raw_question = final_lots["question"]
    segmented_question = textwrap.fill(raw_question, 9)

    l_pos = final_lots["pos"]
    l_rank = final_lots["rank"]
    # l_answer = final_lots["answer"]
    l_question = segmented_question.split("\n")
    l_info = f"第{l_pos}签\u3000\u3000{l_rank}"

    # 绘制时间
    pen.text((95, 135), year, fill="#8d7650ff", font=time_font, anchor="mm")
    pen.text((350, 135), month, fill="#8d7650ff", font=time_font, anchor="mm")
    pen.text((230, 135), day, fill="#f7f8f2ff", font=time_font, anchor="mm")

    # 绘制签的具体信息
    pen.text((350, 375), text_r90(l_info), fill="#711b0f", font=lot_font, anchor="mm")
    for m, n in enumerate(l_question):
        text_x = question_x - lot_font.size * m
        r90t = text_r90(n)
        pen.text((text_x, question_y), r90t, fill="#be0a13", font=lot_font)

    info = {
        "pos": final_lots["pos"],
        "pic": bg
    }
    return info


def get_pic():
    return gen_pic(draw_info(make_draw()))


if __name__ == "__main__":
    print(draw_info("二七"))
