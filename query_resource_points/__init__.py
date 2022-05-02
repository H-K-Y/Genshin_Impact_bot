
from nonebot import on_command,on_regex
from nonebot.typing import T_State
from nonebot.params import State
from nonebot.adapters.onebot.v11 import Message, Bot, Event
from .query_resource_points import get_resource_map_mes,get_resource_list_mes,init_point_list_and_map

inquire_resource = on_regex(r"^哪里有|^哪有|在哪里$|在哪$")
resource_list = on_command('原神资源列表')
up_resource_list = on_command('刷新原神资源列表')
up_map_icon = on_command('更新原神地图')


@inquire_resource.handle()
async def _inquire_resource_(bot: Bot, event: Event, state: T_State = State()):
    resource_name = str(event.get_message()).strip()
    resource_name = resource_name.replace(state["_matched"],"")
    if resource_name == "":
        return
    await inquire_resource.finish(Message(await get_resource_map_mes(resource_name)), at_sender=True)



@resource_list.handle()
async def resource_list_(bot: Bot, event: Event):
    # 长条消息经常发送失败，所以只能这样了
    group_id = event.group_id
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
    await bot.send_group_forward_msg(group_id=group_id, messages=mes_list)


@up_resource_list.handle()
async def up_resource_list_(bot: Bot, event: Event):
    await init_point_list_and_map()
    await up_resource_list.finish('刷新成功', at_sender=True)



@up_map_icon.handle()
async def up_map_icon_(bot: Bot, event: Event):
    await init_point_list_and_map()
    await up_map_icon.finish('更新成功', at_sender=True)

