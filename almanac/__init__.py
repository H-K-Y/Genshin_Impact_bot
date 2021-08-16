from nonebot import on_command,get_bot
from nonebot import require
from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp import GROUP_ADMIN, GROUP_OWNER
from nonebot.adapters.cqhttp import Message
from nonebot.permission import SUPERUSER
from .almanac import get_almanac_base64_str, load_data
from .tweaks import *
from .draw_lots import get_pic, draw_info, gen_pic

import os
import json

get_almanac = on_command('原神黄历')
reload_data = on_command('重载原神黄历数据')
open_remind = on_command('开启原神黄历提醒')
off_remind = on_command("关闭原神黄历提醒")
draw_lots = on_command('原神抽签')
answer_lots = on_command('解签')


FILE_PATH = os.path.dirname(__file__)
DB_PATH = os.path.join(FILE_PATH, "assets", "config.json")
jdb = jsondb(DB_PATH)

group_list = []


def save_group_list():
    with open(os.path.join(FILE_PATH, 'group_list.json'), 'w', encoding='UTF-8') as f:
        json.dump(group_list, f, ensure_ascii=False)


# 检查group_list.json是否存在，没有创建空的
if not os.path.exists(os.path.join(FILE_PATH, 'group_list.json')):
    save_group_list()

# 读取group_list.json的信息
with open(os.path.join(FILE_PATH, 'group_list.json'), 'r', encoding='UTF-8') as f:
    group_list = json.load(f)


@get_almanac.handle()
async def get_almanac_(bot: Bot, event: Event):
    almanac_base64 = get_almanac_base64_str()
    mes = f"[CQ:image,file={almanac_base64}] \n ※ 黄历数据来源于 genshin.pub"
    await get_almanac.finish(Message(mes))


@reload_data.handle()
async def reload_data_(bot: Bot, event: Event):
    if not (await GROUP_ADMIN(bot, event) or
            await GROUP_OWNER(bot, event) or
            (str(event.user_id) in SUPERUSER) ):
        await reload_data.finish('你没有权限这么做', at_sender=True)
        return

    load_data()
    await reload_data.finish("重载成功")


@open_remind.handle()
async def open_remind_(bot: Bot, event: Event):
    if not (await GROUP_ADMIN(bot, event) or
            await GROUP_OWNER(bot, event) or
            (str(event.user_id) in SUPERUSER)):
        await reload_data.finish('你没有权限这么做', at_sender=True)
        return

    gid = str(event.group_id)
    if not (gid in group_list):
        group_list.append(gid)
        save_group_list()
    await open_remind.finish("每日提醒已开启，每天8点会发送今日原神黄历")


@off_remind.handle()
async def off_remind_(bot: Bot, event: Event):
    if not (await GROUP_ADMIN(bot, event) or
            await GROUP_OWNER(bot, event) or
            (str(event.user_id) in SUPERUSER)):
        await reload_data.finish('你没有权限这么做', at_sender=True)
        return

    gid = str(event.group_id)
    if gid in group_list:
        group_list.remove(gid)
        save_group_list()
    await off_remind.finish("每日提醒已关闭")


scheduler = require("nonebot_plugin_apscheduler").scheduler

@scheduler.scheduled_job('cron', hour='8')
async def almanac_remind():
    # 每日提醒
    bot = get_bot()
    almanac_base64 = get_almanac_base64_str()
    mes = f"[CQ:image,file={almanac_base64}] \n ※ 黄历数据来源于 genshin.pub"
    mes = Message(mes)
    for gid in group_list:
        await bot.send_group_msg(group_id=int(gid), message=mes)


@draw_lots.handle()
async def draw_lots_(bot: Bot, event: Event):
    uid = str(event.user_id)
    quser = jdb.user(uid)

    if quser.db["time"] == get_time():
        result = draw_info(quser.pos)
        draw_pic = gen_pic(result)["pic"]
        cq_str = get_cq(draw_pic)
        msg = f"{cq_str}\n今天已经抽过签啦，明天再来吧~\n ※ 抽签条目来源于 genshin.pub"
    else:
        draw_result = get_pic()
        pos = draw_result["pos"]
        pic = draw_result["pic"]
        cq_str = get_cq(pic)

        jdb.user(uid).write(pos)
        jdb.save()
        msg = f"{cq_str}\n ※ 抽签条目来源于 genshin.pub"

    await draw_lots.finish( Message(msg), at_sender=True)


@answer_lots.handle()
async def answer_lots_(bot: Bot, event: Event):
    uid = str(event.user_id)
    quser = jdb.user(uid)

    try:
        answer = draw_info(quser.pos)["answer"]
        msg = f'解签：{answer}\n ※ 解签条目来源于 genshin.pub'
    except KeyError:
        msg = '你还没抽过签哦~向我说“原神抽签”试试吧~'
    await answer_lots.finish((msg), at_sender=True)
