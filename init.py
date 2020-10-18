from hoshino import Service
import gacha

sv = Service('原神抽卡')


@sv.on_prefix(["相遇之源"], only_to_me=True)
async def gacha_10(bot, ev):
    await bot.send(ev, gacha.gacha_10())


