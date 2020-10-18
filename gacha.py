
import os
import json
import random


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
    with open(os.path.join(FILE_PATH,'config.json'),'r', encoding='UTF-8') as f:
        data = json.load(f)
        for key in data.keys():
            ROLE_ARMS_LIST[key] = data[key]
    ROLE_ARMS_LIST["4_role_arms"] =ROLE_ARMS_LIST["4_role"].copy()
    ROLE_ARMS_LIST["4_role_arms"].extend(ROLE_ARMS_LIST["4_arms"])

init_role_arms_list()




def get_png(name):

    role_name_path = os.path.join(ICON_PATH,"角色",str(name) + ".png")
    arms_name_path = os.path.join(ICON_PATH,"武器",str(name) + ".png")
    if os.path.exists(role_name_path):
        return role_name_path

    if os.path.exists(arms_name_path):
        return arms_name_path

    raise IOError(f"找不到 {name} 的图标，请检查图标是否存在")


def is_up(name):
    # 检查角色是否在UP里
    if name in ROLE_ARMS_LIST["5_up"] :
        return True
    if name in ROLE_ARMS_LIST["4_up"] :
        return True
    return False


def get_5_star(last_5 = ""):
    # 先检查上次5星是否是UP，不是UP本次抽取必定是UP，
    # 如果上次是UP，本次有50%的概率还是UP，50%概率所有5星随机
    if is_up(last_5):
        if random.random() > 0.5:
            return random.choice(ROLE_ARMS_LIST["5_up"])
        else:
            return random.choice(ROLE_ARMS_LIST["5_role"])
    else:
        return random.choice(ROLE_ARMS_LIST["5_up"])


def get_4_star(last_4 = ""):
    # 先检查上次4星是否是UP，不是UP本次抽取必定是UP，
    # 如果上次是UP，本次有50%的概率还是UP，50%概率所有5星角色装备随机
    if is_up(last_4):
        if random.random() > 0.5:
            return random.choice(ROLE_ARMS_LIST["4_up"])
        else:
            return random.choice(ROLE_ARMS_LIST["4_role_arms"])
    else:
        return random.choice(ROLE_ARMS_LIST["4_up"])




def gacha(count,last_4 = "",last_5 = ""):
    # count表示，现在抽到多少个了
    # last_4表示上一个4星角色
    # last_5表示上一个5星角色

    r = random.random()

    if count%90 == 0:
        return get_5_star(last_5)

    if r<0.006:
        return get_5_star(last_5)


    if count%10 == 0:
        return get_4_star(last_4)


    if r<0.057:
        return get_4_star(last_4)

    return random.choice(ROLE_ARMS_LIST["3_arms"])


def is_4_star(name):
    if name in ROLE_ARMS_LIST["4_role_arms"] :
        return True
    return False

def is_5_star(name):
    if name in ROLE_ARMS_LIST["5_role"] :
        return True
    return False

def is_star(name):
    # 检查角色或物品是几星的
    if name in ROLE_ARMS_LIST["5_role"]:
        return "★★★★★"
    if name in ROLE_ARMS_LIST["4_role_arms"]:
        return "★★★★"
    return "★★★"


def gacha_10():

    last_4 = ""
    last_5 = ""
    gacha_txt = "本次祈愿得到以下物品：\n"


    for i in range(10):
        new_gacha = gacha(i+1,last_4,last_5)
        gacha_txt += new_gacha
        gacha_txt += is_star(new_gacha)
        gacha_txt += '\n'

        if is_4_star(new_gacha):
            last_4 = new_gacha

        if is_5_star(new_gacha):
            last_5 = new_gacha

    return gacha_txt





