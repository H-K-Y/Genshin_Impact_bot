
from hoshino import Service
from .query_resource_points import get_resource_map_mes,get_resource_list_mes,up_label_and_point_list

sv = Service("原神资源查询")

@sv.on_suffix(('在哪', '在哪里', '哪有', '哪里有'))
@sv.on_prefix(('哪有', '哪里有'))
async def inquire_resource_points(bot, ev):

    resource_name = ev.message.extract_plain_text().strip()
    if resource_name == "":
        return

    await bot.send(ev, get_resource_map_mes(resource_name), at_sender=True)



@sv.on_fullmatch('原神资源列表')
async def inquire_resource_list(bot , ev):
    # 长条消息经常发送失败，所以只能这样了
    mes_list = []
    txt_list = get_resource_list_mes().split("\n")
    for txt in txt_list:
        data = {
            "type": "node",
            "data": {
                "name": "色图机器人",
                "uin": "2854196310",
                "content":txt
                    }
                }
        mes_list.append(data)
    # await bot.send(ev, get_resource_list_mes(), at_sender=True)
    await bot.send_group_forward_msg(group_id=ev['group_id'], messages=mes_list)


@sv.on_fullmatch('刷新原神资源列表')
async def inquire_resource_list(bot , ev):
    up_label_and_point_list()
    await bot.send(ev, '刷新成功', at_sender=True)

