from hoshino import Service,get_bot
from PIL import Image
from io import BytesIO

import os
import json
import time
import base64

sv = Service("原神每日素材提醒")

FILE_PATH = os.path.dirname(__file__)

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

def get_today_material(name:str):
    # 返回今天的材料图片CQ码
    week = time.strftime("%w")

    if week == "0":
        return "今天是周日，所有材料副本都开放了。"
    elif week in ["1","4"]:
        png_name = f"{name}_周一周四.png"
    elif week in ["2","5"]:
        png_name = f"{name}_周二周五.png"
    elif week in ["3","6"]:
        png_name = f"{name}_周三周六.png"

    image = Image.open(os.path.join(FILE_PATH, "icon", png_name))
    bio = BytesIO()
    image.save(bio, format='PNG')
    base64_str = 'base64://' + base64.b64encode(bio.getvalue()).decode()
    return f"[CQ:image,file={base64_str}]"


@sv.on_fullmatch('开启原神每日素材提醒')
async def open_remind(bot , ev):
    gid = str(ev.group_id) if 'group_id' in dir(ev) else str(ev.guild_id)
    if not (gid in group_list):
        group_list.append(gid)
        save_group_list()
    await bot.send(ev, "每日提醒已开启，每天8点会发送今日素材")


@sv.on_fullmatch('关闭原神每日素材提醒')
async def off_remind(bot , ev):
    gid = str(ev.group_id) if 'group_id' in dir(ev) else str(ev.guild_id)
    if gid in group_list:
        group_list.remove(gid)
        save_group_list()
    await bot.send(ev, "每日提醒已关闭")


@sv.on_fullmatch(["今日武器突破材料","今日武器材料","武器材料","今日武器升级材料"])
async def send_arms_material_remind(bot , ev):
    arms_material_CQ = get_today_material("武器突破材料")
    await bot.send(ev, arms_material_CQ)


@sv.on_fullmatch(["今日角色天赋材料","今日角色材料","角色材料","今日天赋升级材料"])
async def send_arms_material_remind(bot , ev):
    roles_material_CQ = get_today_material("角色天赋材料")
    await bot.send(ev, roles_material_CQ)
    
@sv.on_fullmatch(["今日材料","今日素材"])
async def send_arms_material_remind(bot , ev):
    if time.strftime("%w") == "0":
        await bot.send(ev, "今天是周日，所有材料副本都开放了。")
        return
    arms_material_CQ = get_today_material("武器突破材料")
    roles_material_CQ = get_today_material("角色天赋材料")
    await bot.send(ev, arms_material_CQ)
    await bot.send(ev, roles_material_CQ)

@sv.scheduled_job('cron', hour='8')
async def material_remind():
    # 每日提醒
    if time.strftime("%w") == "0":
        # 如果今天是周日就不发了
        return 
    bot = get_bot()
    arms_material_CQ = get_today_material("武器突破材料")
    roles_material_CQ = get_today_material("角色天赋材料")
    for gid in group_list:
        await bot.send_group_msg(group_id=int(gid),message=arms_material_CQ)
        await bot.send_group_msg(group_id=int(gid), message=roles_material_CQ)
        
        