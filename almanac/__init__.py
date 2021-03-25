from hoshino import Service,priv,get_bot
from .almanac import get_almanac_base64_str,load_data
import os
import json


FILE_PATH = os.path.dirname(__file__)

sv = Service("原神黄历")




group_list = []

def save_group_list():
    with open(os.path.join(FILE_PATH,'group_list.json'),'w',encoding='UTF-8') as f:
        json.dump(group_list,f,ensure_ascii=False)

# 检查group_list.json是否存在，没有创建空的
if not os.path.exists(os.path.join(FILE_PATH,'group_list.json')):
    save_group_list()

# 读取group_list.json的信息
with open(os.path.join(FILE_PATH,'group_list.json'),'r',encoding='UTF-8') as f:
    group_list = json.load(f)



@sv.on_fullmatch('原神黄历')
async def send_almanac(bot , ev):
    almanac_base64 = get_almanac_base64_str()
    mes = f"[CQ:image,file={almanac_base64}] \n ※ 黄历数据来源于 genshin.pub"
    await bot.send(ev, mes)



@sv.on_fullmatch('重载原神黄历数据')
async def reload_data(bot , ev):
    if not priv.check_priv(ev, priv.ADMIN):
        return
    load_data()
    await bot.send(ev, "重载成功")


@sv.on_fullmatch('开启原神黄历提醒')
async def open_remind(bot , ev):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.send(ev, "你没有权限这么做")
        return

    gid = str(ev.group_id)
    if not (gid in group_list):
        group_list.append(gid)
        save_group_list()
    await bot.send(ev, "每日提醒已开启，每天8点会发送今日原神黄历")


@sv.on_fullmatch('关闭原神黄历提醒')
async def off_remind(bot , ev):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.send(ev, "你没有权限这么做")
        return

    gid = str(ev.group_id)
    if gid in group_list:
        group_list.remove(gid)
        save_group_list()
    await bot.send(ev, "每日提醒已关闭")


@sv.scheduled_job('cron', hour='8')
async def almanac_remind():
    # 每日提醒
    bot = get_bot()
    almanac_base64 = get_almanac_base64_str()
    mes = f"[CQ:image,file={almanac_base64}] \n ※ 黄历数据来源于 genshin.pub"
    for gid in group_list:
        await bot.send_group_msg(group_id=int(gid),message=mes)

