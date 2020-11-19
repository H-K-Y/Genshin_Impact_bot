

from .Artifact import artifact_obtain,ARTIFACT_LIST,Artifact
from ..config import MAX_STAMINA,STAMINA_RESTORE
from .json_rw import init_user_info,updata_uid_stamina,user_info,save_user_info

from hoshino import Service

import random




sv = Service("原神圣遗物收集")


@sv.on_fullmatch(["原神副本","圣遗物副本","查看原神副本","查看圣遗物副本"])
async def get_obtain(bot, ev):
    mes = "当前副本如下\n"
    for name in artifact_obtain.keys():
        mes += f"{name}\n"
    await bot.send(ev, mes, at_sender=True)

@sv.on_prefix("刷副本")
async def _get_artifact(bot, ev):
    obtain = ev.message.extract_plain_text().strip()
    uid = str(ev['user_id'])
    init_user_info(uid)

    if obtain == "":
        return

    if not (obtain in artifact_obtain.keys()):
        mes = f"没有副本名叫 {obtain} ,发送 原神副本 可查看所有副本"
        await bot.send(ev, mes, at_sender=True)
        return

    if user_info[uid]["stamina"] < 20:
        await bot.send(ev, "体力值不足，请等待体力恢复.\n发送 查看体力值 可查看当前体力", at_sender=True)
        return

    # 随机掉了几个圣遗物
    r = random.randint(1,3)
    # 随机获得的狗粮点数
    strengthen_points = random.randint(70000,100000)
    user_info["strengthen_points"] += strengthen_points

    mes = f"本次刷取副本为 {obtain} \n掉落圣遗物 {r} 个\n获得狗粮点数 {strengthen_points}\n\n"

    for _ in range(r):
        # 随机一个副本掉落的套装名字,然后随机部件的名字
        r_suit_name = random.random(artifact_obtain[obtain])
        r_artifact_name = random.random(ARTIFACT_LIST[r_suit_name]["element"])

        artifact = Artifact(r_artifact_name)

        number = int(len(user_info["warehouse"])) + 1

        mes += f"当前仓库编号 {number}\n"
        mes += artifact.get_artifact_text()
        mes += "\n"

        user_info["warehouse"].append(artifact.get_artifact_dict())

    save_user_info()
    await bot.send(ev, mes, at_sender=True)




@sv.on_prefix("查看圣遗物仓库")
async def _get_warehouse(bot, ev):
    page = ev.message.extract_plain_text().strip()
    uid = str(ev['user_id'])
    init_user_info(uid)

    if not page.isdigit():
        await bot.send(ev, "你需要输入一个数字", at_sender=True)
        return

    if page == "":
        page = 1
    else:
        page = int(page)

    mes = "仓库如下\n"
    txt = ""

    for i in range(5):
        try:
            ar = user_info[uid]["warehouse"][i+(page-1)*5]
            artifact = Artifact(ar)
            txt += f"\n仓库圣遗物编号 {i+(page-1)*5+1}"
            txt += artifact.get_artifact_text()

        except IndexError:
            pass

    if txt == "":
        txt = "当前页数没有圣遗物"

    mes += txt

    await bot.send(ev, mes, at_sender=True)



@sv.on_prefix("转换狗粮")
async def _transform_strengthen(bot, ev):
    number = ev.message.extract_plain_text().strip()
    uid = str(ev['user_id'])
    init_user_info(uid)

    del user_info[uid]["warehouse"][int(number)]
    save_user_info()
    await bot.send(ev, "已删除", at_sender=True)








@sv.on_prefix('氪体力')
async def kakin(bot, ev):
    if ev.user_id not in bot.config.SUPERUSERS:
        return

    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            uid = str(m.data['qq'])
            init_user_info(uid)
            user_info[uid]["stamina"] += 60
    save_user_info()
    await bot.send(ev,f"充值完毕！谢谢惠顾～")





