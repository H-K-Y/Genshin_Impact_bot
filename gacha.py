from PIL import Image
from io import BytesIO
from nonebot import MessageSegment

import os
import json
import random
import math
import base64



FILE_PATH = os.path.dirname(__file__)
ICON_PATH = os.path.join(FILE_PATH,'icon')
ROLE_ARMS_LIST = {
    "5_up":[],
    "4_up":[],
    "5_role":[],
    "4_role":[],
    "4_arms":[],
    "3_arms":[],
    "4_role_arms":[],
}




def init_role_arms_list():
    # 初始化卡池数据
    with open(os.path.join(FILE_PATH,'config.json'),'r', encoding='UTF-8') as f:
        data = json.load(f)
        for key in data.keys():
            ROLE_ARMS_LIST[key] = data[key]
    ROLE_ARMS_LIST["4_role_arms"] =ROLE_ARMS_LIST["4_role"].copy()
    ROLE_ARMS_LIST["4_role_arms"].extend(ROLE_ARMS_LIST["4_arms"])

init_role_arms_list()




def get_png(name):
    # 获取png文件路径，传入的参数是角色或武器名字，会自动在角色和武器文件夹搜索，找不到抛出异常

    role_name_path = os.path.join(ICON_PATH,"角色",str(name) + ".png")
    arms_name_path = os.path.join(ICON_PATH,"武器",str(name) + ".png")
    if os.path.exists(role_name_path):
        return role_name_path

    if os.path.exists(arms_name_path):
        return arms_name_path

    raise IOError(f"找不到 {name} 的图标，请检查图标是否存在")



def gacha_info():
    # 重载卡池数据，然后返回UP角色信息
    init_role_arms_list() # 重新载入config.json的卡池数据
    info_txt = '当前UP池如下：\n'

    for _5_star in ROLE_ARMS_LIST["5_up"]:
        im = Image.open(get_png(_5_star))
        im = pic2b64(im)
        info_txt += str(MessageSegment.image(im))
        info_txt += "\n"
        info_txt += f"{_5_star} ★★★★★"

    for _4_star in ROLE_ARMS_LIST["4_up"]:
        # info_txt += f"[CQ:image,file=file://{get_png(_4_star)}]"
        im = Image.open(get_png(_4_star))
        im = pic2b64(im)
        info_txt += str(MessageSegment.image(im))
        info_txt += "\n"
        info_txt += f"{_4_star} ★★★★"

    return info_txt





def is_up(name):
    # 检查角色是否在UP里
    # 如果name是一个空字符串表示是第一次抽到4星或5星
    if name == "":
        return True
    if name in ROLE_ARMS_LIST["5_up"] :
        return True
    if name in ROLE_ARMS_LIST["4_up"] :
        return True
    return False


def get_5_star(last_time_5 = ""):
    # 先检查上次5星是否是UP，不是UP本次抽取必定是UP，
    # 如果上次是UP，本次有50%的概率还是UP，50%概率所有5星随机
    if is_up(last_time_5):
        if random.random() > 0.5:
            return random.choice(ROLE_ARMS_LIST["5_up"])
        else:
            return random.choice(ROLE_ARMS_LIST["5_role"])
    else:
        return random.choice(ROLE_ARMS_LIST["5_up"])


def get_4_star(last_time_4 = ""):
    # 先检查上次4星是否是UP，不是UP本次抽取必定是UP，
    # 如果上次是UP，本次有50%的概率还是UP，50%概率所有5星角色装备随机
    if is_up(last_time_4):
        if random.random() > 0.5:
            return random.choice(ROLE_ARMS_LIST["4_up"])
        else:
            return random.choice(ROLE_ARMS_LIST["4_role_arms"])
    else:
        return random.choice(ROLE_ARMS_LIST["4_up"])




def gacha(count,last_time_4 = "",last_time_5 = ""):
    # count表示，现在抽到多少个了
    # last_4表示上一个4星角色
    # last_5表示上一个5星角色

    r = random.random()

    # 先检查是不是保底5星
    if count%90 == 0:
        return get_5_star(last_time_5)

    # 检查是不是概率5星
    if r<0.006:
        return get_5_star(last_time_5)

    # 检查是不是保底4星
    if count%10 == 0:
        return get_4_star(last_time_4)

    # 检查是不是概率4星
    if r<0.057:
        return get_4_star(last_time_4)

    # 以上都不是返回3星
    return random.choice(ROLE_ARMS_LIST["3_arms"])


def is_4_star(name):
    # 判断角色是不是4星
    if name in ROLE_ARMS_LIST["4_role_arms"] :
        return True
    return False

def is_5_star(name):
    # 判断角色是不是5星
    if name in ROLE_ARMS_LIST["5_role"] :
        return True
    return False

def is_star(name):
    # 检查角色或物品是几星的
    # 返回对应就星星数
    if name in ROLE_ARMS_LIST["5_role"]:
        return "★★★★★"
    if name in ROLE_ARMS_LIST["4_role_arms"]:
        return "★★★★"
    return "★★★"


def concat_pic(name_list, border=5):
    # pics是一个列表，这个函数找到列表中名字的图片，然后拼接成一张大图返回
    num = len(name_list)
    # w, h = pics[0].size
    w, h = [125,130]
    des = Image.new('RGBA', (w * min(num,border), h * math.ceil(num/border)), (255, 255, 255, 0))



    for i in range(num):
        im = Image.open(get_png(name_list[i]))

        pixel_w_offset = (125 - im.size[0])/2
        pixel_h_offset = (130 - im.size[1])/2  # 因为角色和武器大小不一样，小的图像设置居中显示

        w_row = (i % border) + 1
        h_row = math.ceil((i + 1 ) / border)

        pixel_w = (w_row-1) * w + pixel_w_offset
        pixel_h = (h_row-1) * h + pixel_h_offset

        des.paste(im, (int(pixel_w), int(pixel_h)))

    return des



def pic2b64(pic:Image) -> str:
    buf = BytesIO()
    pic.save(buf, format='PNG')
    base64_str = base64.b64encode(buf.getvalue()).decode()
    return 'base64://' + base64_str



def gacha_10():
    # 抽10连

    last_time_4 = ""
    last_time_5 = ""
    gacha_txt = ""
    gacha_list = []


    last_4_up = 0
    last_5_up = 0 # 记录多少抽出现UP



    for i in range(10):
        new_gacha = gacha(i+1,last_time_4,last_time_5)
        gacha_list.append(new_gacha)
        gacha_txt += new_gacha
        gacha_txt += is_star(new_gacha)
        if (i+1)%5 ==  0:
            gacha_txt += '\n'

        if is_4_star(new_gacha):
            last_time_4 = new_gacha

        if is_5_star(new_gacha):
            last_time_5 = new_gacha

        if not last_4_up:
            if new_gacha in ROLE_ARMS_LIST['4_up']:
                last_4_up = i+1

        if not last_5_up:
            if new_gacha in ROLE_ARMS_LIST['5_up']:
                last_5_up = i+1

    mes = '本次祈愿得到以下角色装备：\n'
    res = concat_pic(gacha_list)
    res = pic2b64(res)
    mes += str(MessageSegment.image(res))
    mes += '\n'
    mes += gacha_txt

    if last_4_up:
        mes += f'第 {last_4_up} 抽首次出现4★UP!'
        mes += '\n'
    if last_5_up:
        mes += f'第 {last_5_up} 抽首次出现5★UP!'

    return mes


def gacha_90(frequency = 90):
    # 抽一井

    last_time_4 = ""
    last_time_5 = ""
    gacha_txt = ""
    gacha_list = []


    last_4_up = 0
    last_5_up = 0 # 记录多少抽出现UP

    gacha_statistics = {
        '3_star' : 0,
        '4_star' : 0,
        '5_star' : 0
    }


    for i in range(frequency):
        new_gacha = gacha(i+1,last_time_4,last_time_5)

        if new_gacha in ROLE_ARMS_LIST['3_arms']:
            gacha_statistics['3_star'] += 1

        if new_gacha in ROLE_ARMS_LIST["4_role_arms"]:
            gacha_statistics['4_star'] += 1
            gacha_list.append(new_gacha)

        if new_gacha in ROLE_ARMS_LIST["5_role"]:
            gacha_statistics['5_star'] += 1
            gacha_list.append(new_gacha)


        if is_4_star(new_gacha):
            last_time_4 = new_gacha

        if is_5_star(new_gacha):
            last_time_5 = new_gacha

        if not last_4_up:
            if new_gacha in ROLE_ARMS_LIST['4_up']:
                last_4_up = i+1

        if not last_5_up:
            if new_gacha in ROLE_ARMS_LIST['5_up']:
                last_5_up = i+1

    gacha_txt +=f"★★★★★*{gacha_statistics['5_star']}    ★★★★*{gacha_statistics['4_star']}    ★★★*{gacha_statistics['3_star']}\n"

    mes = '本次祈愿得到以下角色装备：\n'
    res = concat_pic(gacha_list)
    res = pic2b64(res)
    mes += str(MessageSegment.image(res))
    mes += '\n'
    mes += gacha_txt

    if last_4_up:
        mes += f'第 {last_4_up} 抽首次出现4★UP!'
        mes += '\n'
    if last_5_up:
        mes += f'第 {last_5_up} 抽首次出现5★UP!'

    return mes


