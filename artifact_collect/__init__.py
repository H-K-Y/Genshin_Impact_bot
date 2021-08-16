from nonebot import on_command,on_startswith
from nonebot import require
from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp import Message
from nonebot.permission import SUPERUSER

from .Artifact import artifact_obtain, ARTIFACT_LIST, Artifact, calculate_strengthen_points
from ..config import STAMINA_RESTORE, MAX_STAMINA
from .json_rw import init_user_info, updata_uid_stamina, user_info, save_user_info
import random

get_obtain = on_command(("原神副本", "圣遗物副本", "查看原神副本", "查看圣遗物副本"))
get_artifact = on_startswith("刷副本")
get_warehouse = on_startswith("查看圣遗物仓库")
strengthen_artifact = on_startswith("强化圣遗物")
artifact_info = on_startswith("圣遗物详情")
artifact_re_init = on_startswith("圣遗物洗点")
transform = on_startswith(("转换狗粮", "转化狗粮"))
transform_all = on_command(("转化全部0级圣遗物", "转换全部0级圣遗物"))
get_user_stamina = on_command("查看体力值")
recharge = on_command("氪体力")



@get_obtain.handle()
async def get_obtain_(bot: Bot, event: Event):
    mes = "当前副本如下\n"
    for name in artifact_obtain.keys():
        suits = " ".join(artifact_obtain[name])
        mes += f"{name}  掉落  {suits}\n"
    await get_obtain.finish(mes, at_sender=True)


@get_artifact.handle()
async def get_artifact_(bot: Bot, event: Event):
    obtain = str(event.get_message()).strip()
    uid = str(event.user_id)
    init_user_info(uid)

    if obtain == "":
        return

    if not (obtain in artifact_obtain.keys()):
        mes = f"没有副本名叫 {obtain} ,发送 原神副本 可查看所有副本"
        await get_artifact.finish(mes, at_sender=True)
        return

    if user_info[uid]["stamina"] < 20:
        await get_artifact.finish("体力值不足，请等待体力恢复.\n发送 查看体力值 可查看当前体力", at_sender=True)
        return

    user_info[uid]["stamina"] -= 20
    # 随机掉了几个圣遗物
    r = random.randint(1, 3)
    # 随机获得的狗粮点数
    strengthen_points = random.randint(70000, 100000)
    user_info[uid]["strengthen_points"] += strengthen_points

    mes = f"本次刷取副本为 {obtain} \n掉落圣遗物 {r} 个\n获得狗粮点数 {strengthen_points}\n\n"

    for _ in range(r):
        # 随机一个副本掉落的套装名字,然后随机部件的名字
        r_suit_name = random.choice(artifact_obtain[obtain])
        r_artifact_name = random.choice(ARTIFACT_LIST[r_suit_name]["element"])

        artifact = Artifact(r_artifact_name)

        number = int(len(user_info[uid]["warehouse"])) + 1

        # mes += f"当前仓库编号 {number}\n"
        mes += artifact.get_artifact_CQ_code(number)
        mes += "\n"

        user_info[uid]["warehouse"].append(artifact.get_artifact_dict())

    save_user_info()
    await get_artifact.finish(Message(mes), at_sender=True)


@get_warehouse.handle()
async def get_warehouse_(bot: Bot, event: Event):
    page = str(event.get_message()).strip()
    uid = str(event.user_id)
    init_user_info(uid)
    if page == "":
        page = "1"

    if not page.isdigit():
        await get_warehouse.finish("你需要输入一个数字", at_sender=True)
        return

    page = int(page)

    mes = "仓库如下\n"
    txt = ""

    for i in range(5):
        try:
            ar = user_info[uid]["warehouse"][i + (page - 1) * 5]
            artifact = Artifact(ar)
            number = i + (page - 1) * 5 + 1
            # txt += f"\n\n仓库圣遗物编号 {i+(page-1)*5+1}"
            txt += artifact.get_artifact_CQ_code(number)

        except IndexError:
            pass

    if txt == "":
        txt = "当前页数没有圣遗物"

    mes += txt
    mes += f"\n\n当前为仓库第 {page} 页，你的仓库共有 {(len(user_info[uid]['warehouse']) // 5) + 1} 页"

    await get_warehouse.finish(Message(mes), at_sender=True)


@strengthen_artifact.handle()
async def strengthen_artifact_(bot: Bot, event: Event):
    uid = str(event.user_id)
    init_user_info(uid)

    try:
        txt = str(event.get_message()).replace(" ", "")
        strengthen_level, number = txt.split("级")

    except Exception:
        await strengthen_artifact.finish("指令格式错误", at_sender=True)
        return

    try:
        artifact = user_info[uid]["warehouse"][int(number) - 1]
    except IndexError:
        await strengthen_artifact.finish("圣遗物编号错误", at_sender=True)
        return

    strengthen_level = int(strengthen_level)
    artifact = Artifact(artifact)
    strengthen_point = calculate_strengthen_points(artifact.level + 1, artifact.level + strengthen_level)

    if strengthen_point > user_info[uid]["strengthen_points"]:
        await strengthen_artifact.finish(
                       "狗粮点数不足\n你可以发送 刷副本 副本名称 获取狗粮点数\n或者发送 转换狗粮 圣遗物编号 销毁仓库里不需要的圣遗物获取狗粮点数\n发送 转换全部0级圣遗物 可将全部0级圣遗物销毁",
                       at_sender=True)
        return

    user_info[uid]["strengthen_points"] -= strengthen_point

    for _ in range(strengthen_level):
        artifact.strengthen()

    mes = "强化成功，当前圣遗物属性为：\n"
    mes += artifact.get_artifact_detail()

    user_info[uid]["warehouse"][int(number) - 1] = artifact.get_artifact_dict()
    save_user_info()
    await strengthen_artifact.finish(Message(mes), at_sender=True)


@artifact_info.handle()
async def artifact_info_(bot: Bot, event: Event):
    number = str(event.get_message()).strip()
    uid = str(event.user_id)
    init_user_info(uid)

    try:
        artifact = user_info[uid]["warehouse"][int(number) - 1]
    except IndexError:
        await artifact_info.finish("编号错误", at_sender=True)
        return

    artifact = Artifact(artifact)
    await artifact_info.finish(Message(artifact.get_artifact_detail()), at_sender=True)


@artifact_re_init.handle()
async def artifact_re_init_(bot: Bot, event: Event):
    number = str(event.get_message()).strip()
    uid = str(event.user_id)
    init_user_info(uid)

    try:
        artifact = user_info[uid]["warehouse"][int(number) - 1]
    except IndexError:
        await artifact_re_init.finish("编号错误", at_sender=True)
        return

    artifact = Artifact(artifact)

    if artifact.level < 20:
        await artifact_re_init.finish("没有强化满的圣遗物不能洗点", at_sender=True)
        return

    strengthen_points = calculate_strengthen_points(1, artifact.level)
    strengthen_points = int(strengthen_points * 0.5)

    artifact.re_init()
    user_info[uid]["warehouse"][int(number) - 1] = artifact.get_artifact_dict()

    user_info[uid]["strengthen_points"] += strengthen_points

    mes = f"洗点完成，获得返还狗粮 {strengthen_points} \n当前圣遗物属性如下：\n"
    mes += artifact.get_artifact_detail()
    save_user_info()

    await artifact_re_init.finish(Message(mes), at_sender=True)


@transform.handle()
async def transform_(bot: Bot, event: Event):
    number = str(event.get_message()).strip()
    uid = str(event.user_id)
    init_user_info(uid)

    try:
        artifact = user_info[uid]["warehouse"][int(number) - 1]
    except IndexError:
        await transform.finish("编号错误", at_sender=True)
        return
    artifact = Artifact(artifact)

    strengthen_points = calculate_strengthen_points(0, artifact.level)
    strengthen_points = int(strengthen_points * 0.8)

    del user_info[uid]["warehouse"][int(number) - 1]

    user_info[uid]["strengthen_points"] += strengthen_points

    save_user_info()

    mes = f"转化完成，圣遗物已转化为 {int(strengthen_points)} 狗粮点数\n你当前狗粮点数为 {int(user_info[uid]['strengthen_points'])} "
    await transform.finish(Message(mes), at_sender=True)


@get_user_stamina.handle()
async def get_user_stamina_(bot: Bot, event: Event):
    uid = str(event.user_id)
    init_user_info(uid)
    mes = f"你当前的体力值为 {int(user_info[uid]['stamina'])} ,体力值每 {STAMINA_RESTORE} 分钟恢复1点，自动恢复上限为 {MAX_STAMINA}\n"
    mes += f"你当前的狗粮点数为 {int(user_info[uid]['strengthen_points'])}"
    await get_user_stamina.finish(Message(mes), at_sender=True)


@recharge.handle()
async def recharge_(bot: Bot, event: Event):
    if not (str(event.user_id) in SUPERUSER):
        await recharge.finish(f"这个指令仅限超级管理员使用")
        return
    for m in event.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            uid = str(m.data['qq'])
            init_user_info(uid)
            user_info[uid]["stamina"] += 60
    save_user_info()
    await recharge.finish(f"充值完毕！谢谢惠顾～")


@transform_all.handle()
async def transform_all_(bot: Bot, event: Event):
    uid = str(event.user_id)
    init_user_info(uid)

    _0_level_artifact = 0
    temp_list = []

    for artifact in user_info[uid]["warehouse"]:
        if artifact["level"] == 0:
            _0_level_artifact += 1
        else:
            temp_list.append(artifact)

    strengthen_points = _0_level_artifact * 3024

    user_info[uid]["warehouse"] = temp_list
    user_info[uid]["strengthen_points"] += strengthen_points
    save_user_info()

    await transform_all.finish(f"0级圣遗物已全部转化为狗粮，共转化 {_0_level_artifact} 个圣遗物，获得狗粮点数 {strengthen_points}")



updata_stamina = require("nonebot_plugin_apscheduler").scheduler

@updata_stamina.scheduled_job('interval', minutes=STAMINA_RESTORE)
async def _call():
    updata_uid_stamina()
