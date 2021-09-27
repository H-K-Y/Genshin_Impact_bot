from nonebot import on_command,on_startswith
from nonebot.rule import to_me
from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp import GROUP_ADMIN, GROUP_OWNER
from nonebot.adapters.cqhttp import Message
from nonebot.permission import SUPERUSER
from .gacha import gacha_info , FILE_PATH , Gacha
from .pool_data import POOL, init_pool_list
import os
import json


gacha_10 = on_command(("相遇之缘",), rule=to_me())
gacha_90 = on_command(("纠缠之缘",), rule=to_me())
gacha_180 = on_command(("原之井",), rule=to_me())
look_pool = on_command(cmd="查看原神卡池",aliases = {"查看原神up","查看原神UP"})
set_pool = on_startswith(('原神卡池切换','原神切换卡池'))
up_pool_data = on_command('更新原神卡池')

group_pool = {
    # 这个字典保存每个群对应的卡池是哪个，群号字符串为key,卡池名为value，群号不包含在字典key里卡池按默认DEFAULT_POOL
}

def save_group_pool():
    with open(os.path.join(FILE_PATH,'gid_pool.json'),'w',encoding='UTF-8') as f:
        json.dump(group_pool,f,ensure_ascii=False)



# 检查gid_pool.json是否存在，没有创建空的
if not os.path.exists(os.path.join(FILE_PATH,'gid_pool.json')):
    save_group_pool()



# 读取gid_pool.json的信息
with open(os.path.join(FILE_PATH,'gid_pool.json'),'r',encoding='UTF-8') as f:
    group_pool = json.load(f)




@gacha_10.handle()
async def gacha_10_(bot: Bot, event: Event):
    gid = str(event.group_id)

    if gid in group_pool:
        G = Gacha(group_pool[gid])
    else:
        G = Gacha()

    await gacha_10.finish(Message(G.gacha_10()) , at_sender=True)

@gacha_90.handle()
async def gacha_90_(bot: Bot, event: Event):
    gid = str(event.group_id)

    if gid in group_pool:
        G = Gacha(group_pool[gid])
    else:
        G = Gacha()
    await gacha_90.finish(Message(G.gacha_90(90)) , at_sender=True)



@gacha_180.handle()
async def gacha_180_(bot: Bot, event: Event):
    gid = str(event.group_id)

    if gid in group_pool:
        G = Gacha(group_pool[gid])
    else:
        G = Gacha()
    await gacha_180.finish(Message(G.gacha_90(180)) , at_sender=True)



@look_pool.handle()
async def look_pool_(bot: Bot, event: Event):
    gid = str(event.group_id)

    if gid in group_pool:
        info = gacha_info(group_pool[gid])
    else:
        info = gacha_info()

    await look_pool.finish(Message(info) , at_sender=True)

@set_pool.handle()
async def set_pool_(bot: Bot, event: Event):

    if not (await GROUP_ADMIN(bot, event) or
            await GROUP_OWNER(bot, event) or
            (str(event.user_id) in SUPERUSER) ):
        await set_pool.finish('只有群管理才能切换卡池', at_sender=True)
        return

    pool_name = str(event.get_message()).strip()
    gid = str(event.group_id)

    if pool_name in POOL.keys():
        if gid in group_pool:
            group_pool[gid] = pool_name
        else:
            group_pool.setdefault(gid,pool_name)
        save_group_pool()
        await set_pool.finish(f"卡池已切换为 {pool_name} ")
        return

    txt = "请使用以下命令来切换卡池\n"
    for i in POOL.keys():
        txt += f"原神卡池切换 {i} \n"

    await set_pool.finish(txt)



@up_pool_data.handle()
async def up_pool_pata_(bot: Bot):
    await up_pool_data.finish("正在更新卡池")
    await init_pool_list()
    await up_pool_data.finish("更新完成")



