
import os
import json

from ..config import MAX_STAMINA

FILE_PATH = os.path.dirname(__file__)
USER_INFO_PATH = os.path.join(FILE_PATH,"user_info.json")


user_info = {}


def save_user_info():
    with open(USER_INFO_PATH,'w',encoding='UTF-8') as f:
        json.dump(user_info,f,ensure_ascii=False)

# 检查user_info.json是否存在，没有创建空的
if not os.path.exists(USER_INFO_PATH):
    save_user_info()

# 读取user_info.json的信息
with open(USER_INFO_PATH,'r',encoding='UTF-8') as f:
    user_info = json.load(f)


def init_user_info(uid:str):
    if not (uid in user_info):
        user_info[uid] = {}
        user_info[uid]["stamina"] = 120
        user_info[uid]["strengthen_points"] = 0
        user_info[uid]["warehouse"] = []

        save_user_info()

def updata_uid_stamina():
    # 更新体力值恢复，这个函数执行一次所有人体力值+1
    for uid in user_info:
        if user_info[uid]["stamina"] < MAX_STAMINA:
            user_info[uid]["stamina"] += 1
    save_user_info()





