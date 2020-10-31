
from hoshino import Service
from .query_resource_points import get_resource_map_mes,get_resource_list_mes

sv = Service("原神资源图")

@sv.on_suffix(('在哪', '在哪里', '哪有', '哪里有'))
@sv.on_prefix(('哪有', '哪里有'))
async def inquire_resource_points(bot, ev):

    resource_name = ev.message.extract_plain_text().strip()
    if resource_name == "":
        return

    await bot.send(ev, get_resource_map_mes(resource_name), at_sender=True)

@sv.on_fullmatch('原神资源列表')
async def inquire_resource_list(bot , ev):
    await bot.send(ev, get_resource_list_mes(), at_sender=True)
