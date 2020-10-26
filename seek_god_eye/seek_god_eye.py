
from PIL import Image
from io import BytesIO

import os
import json
import random
import base64

FILE_PATH = os.path.dirname(__file__)

JSON_LIST = ["风神瞳","岩神瞳"]

PNG_NAME = {
    # 属性对应的神瞳图片
    "风神瞳":"wind_god_eye.png",
    "岩神瞳":"rock_god_eye.png"
}

GOD_EYE_TOTAL = {
    # 每种神瞳有多少个，这个字典会在导入神瞳的json时初始化
    # "风神瞳" : 100
}

GOD_EYE_INFO = {
    # 所有神瞳的信息
    # "56": {
    #     "属性": "风神瞳",
    #     "gif_url": "https://uploadstatic.mihoyo.com/ys-obc/2020/09/21/76373921/cbd63e9fbb00160b045dafc424c1657f_1299454333660281584.gif",
    #     "备注": "",
    #     "x_pos": 1922.0018670150284,
    #     "y_pos": 683.9995073891628
    # }
}

GOD_EYE_CLASS_LIST = {
    # 每种神瞳的编号列表
    # "风神瞳":["1","2","3"],
    # "岩神瞳":["4","5","6"]

}


MAP_IMAGE = Image.open(os.path.join(FILE_PATH,"icon","map_icon.png"))
MAP_SIZE = MAP_IMAGE.size


# 风神瞳.json里记录的坐标是相对坐标，是以蒙德城的大雕像为中心的，所以图片合成时需要转换坐标
CENTER = (3505,1907)


uid_info = {
    # 这个字典记录用户已经找到的神瞳编号
    # "12345":{
    #     "风神瞳":[],
    #     "岩神瞳":[]
    # }
}



for json_name in JSON_LIST:
    # 导入神瞳的.json文件
    with open(os.path.join(FILE_PATH, f"{json_name}.json"), 'r', encoding='UTF-8') as f:
        data = json.load(f)
        GOD_EYE_TOTAL[json_name] = len(data)
        GOD_EYE_INFO.update(data)
        GOD_EYE_CLASS_LIST.setdefault(json_name,data.keys())




def save_uid_info():
    with open(os.path.join(FILE_PATH,'uid_info.json'),'w',encoding='UTF-8') as f:
        json.dump(uid_info,f,ensure_ascii=False)


# 检查uid_info.json是否存在，没有创建空的
if not os.path.exists(os.path.join(FILE_PATH,'uid_info.json')):
    save_uid_info()

# 读取uid_info.json的信息
with open(os.path.join(FILE_PATH,'uid_info.json'),'r',encoding='UTF-8') as f:
    uid_info = json.load(f)





class God_eye_position_image(object):

    def __init__(self,god_eye_id):
        self.id = str(god_eye_id)

        # ID对应的png文件名
        self.png_name = PNG_NAME[GOD_EYE_INFO[self.id]["属性"]]

        # 复制一份地图文件
        self.map_image = MAP_IMAGE.copy()

        # 神瞳的坐标
        self.x,self.y = self.transform_position()

        # 神瞳图片在paste时的偏移量
        self.offset = [25,60]

    def transform_position(self):
        # 风神瞳.json里记录的坐标是相对坐标,需要转换一下
        x = GOD_EYE_INFO[self.id]["x_pos"] + CENTER[0]
        y = GOD_EYE_INFO[self.id]["y_pos"] + CENTER[1]
        return [int(x),int(y)]

    def get_crop_pos(self):
        # 返回地图的裁切尺寸，检查裁切点是否越界
        x = max(self.x - 500,0)
        y = max(self.y - 500,0)
        r = min(self.x + 500,MAP_SIZE[0])
        l = min(self.y + 500,MAP_SIZE[1])
        return [x,y,r,l]

    def paste(self):
        god_eye_image = Image.open(os.path.join(FILE_PATH, "icon", self.png_name))
        self.map_image.paste(god_eye_image,(self.x - self.offset[0],self.y - self.offset[1]),god_eye_image)
        self.map_image = self.map_image.crop(self.get_crop_pos())

    def get_cq_code(self):
        self.paste()
        bio = BytesIO()
        self.map_image.save(bio, format='PNG')
        base64_str = 'base64://' + base64.b64encode(bio.getvalue()).decode()

        return f"[CQ:image,file={base64_str}]"



def get_uid_number_found(uid:str,eye_type:str):
    number = 0
    if uid in uid_info:
        number = len(uid_info[uid][eye_type])
    return f"你已经找到了 {number} 个 {eye_type} ,该神瞳一共有 {GOD_EYE_TOTAL[eye_type]} 个!"


def get_eye_gif_path(eye_id):
    # 获取gif的路径，找不到会返回空字符串
    eye_type = GOD_EYE_INFO[eye_id]["属性"]
    gif_path = os.path.join(FILE_PATH,"icon",eye_type,str(eye_id) + ".gif")
    if os.path.exists(gif_path):
        return gif_path
    else:
        return ""


def get_eye_gif_cq_code(eye_id):
    # 获取gif的CQ码，找不到gif文件会返回空字符串
    gif_path = get_eye_gif_path(eye_id)
    if gif_path == "":
        return ""

    gif_path = gif_path.replace("\\","/")
    cq_code = f'[CQ:image,file={gif_path}]'
    return cq_code

def get_eye_remarks(eye_id):
    # 获取神瞳的备注，注意有的神瞳备注是空字符串
    return GOD_EYE_INFO[eye_id]["备注"]

def add_god_eye_info(uid,eye_id):
    eye_type = GOD_EYE_INFO[eye_id]["属性"]
    uid_info[uid][eye_type].append(eye_id)
    save_uid_info()

def init_uid_info(uid):
    # 初始化用户的信息
    if not (uid in uid_info):
        uid_info.setdefault(uid, {})
    for eye_type in JSON_LIST:
        if not (eye_type in uid_info[uid]):
            uid_info[uid].setdefault(eye_type, [])

def get_random_god_eye_id(uid,eye_type):
    # 获取一个随机没找到过的神瞳ID，返回随机到的神瞳ID，如果返回空字符串表示这种神瞳已经全部找到了
    if len(uid_info[uid][eye_type]) == GOD_EYE_TOTAL[eye_type]:
        return ""
    # 求差集找出没找到过的神瞳列表
    eyes_never_found = set(GOD_EYE_CLASS_LIST[eye_type]).difference(set(uid_info[uid][eye_type].keys()))
    r = random.choice(eyes_never_found)
    return str(r)

def delete_god_eye_info(uid,eye_id):
    eye_type = GOD_EYE_INFO[eye_id]["属性"]
    if not (eye_id in uid_info[uid][eye_type]):
        return "你还没有找到这个神瞳！"

    uid_info[uid][eye_type].remove(eye_id)
    save_uid_info()
    return f"已经在你的记录列表删除编号为 {eye_id} 的神瞳"

def reset_god_eye_info(uid,eye_type):
    # 重置某一种神瞳的已找到列表
    uid_info[uid][eye_type] = []
    save_uid_info()
    return "已重置已找到这种神瞳的列表"

def get_god_eye_message(eye_id):
    message = f"当前神瞳编号 {eye_id} \n"
    message += God_eye_position_image(eye_id).get_cq_code()
    message += get_eye_gif_cq_code(eye_id)
    message += get_eye_remarks(eye_id)
    message += "\n"
    message += "※ 如果你找到了神瞳或者你确定这个神瞳已经找过了，可以发送 找到神瞳了 神瞳编号\n"
    message += "※ 机器人将不再给你发送这个神瞳位置"
    message += "※ 图片及数据来源于原神官方wiki"

def found_god_eye(uid,eye_id):
    add_god_eye_info(uid,eye_id)
    save_uid_info()
    return f"已添加编号为 {eye_id} 的神瞳找到记录！"


