from hoshino import Service
from .qiu_qiu_translation import qiu_qiu_word_translation,qiu_qiu_phrase_translation


sv = Service("原神丘丘语翻译")

suffix = "\n※ 这个插件只能从丘丘语翻译为中文，不能反向翻译\n※ 发送词语时请注意空格位置是否正确，词语不区分大小写，不要加入任何标点符号\n※ 翻译数据来源于 米游社论坛 https://bbs.mihoyo.com/ys/article/2286805 \n※ 如果你有更好的翻译欢迎来提出 issues"



@sv.on_prefix("丘丘一下")
async def qiu_qiu(bot, ev):
    txt = ev.message.extract_plain_text().strip().lower()
    if txt == "":
        return
    mes = qiu_qiu_word_translation(txt)
    mes += suffix
    await bot.send(ev, mes,at_sender=True)



@sv.on_prefix("丘丘词典")
async def qiu_qiu(bot, ev):
    txt = ev.message.extract_plain_text().strip().lower()
    if txt == "":
        return
    mes = qiu_qiu_phrase_translation(txt)
    mes += suffix
    await bot.send(ev, mes,at_sender=True)







