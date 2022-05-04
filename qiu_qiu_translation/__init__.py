from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Event
from .qiu_qiu_translation import qiu_qiu_word_translation,qiu_qiu_phrase_translation

qiu_qiu = on_command("丘丘一下")
qiu_qiu_dictionary = on_command("丘丘词典")


suffix = "\n※ 这个插件只能从丘丘语翻译为中文，不能反向翻译\n※ 发送词语时请注意空格位置是否正确，词语不区分大小写，不要加入任何标点符号\n※ 翻译数据来源于 米游社论坛 https://bbs.mihoyo.com/ys/article/2286805 \n※ 如果你有更好的翻译欢迎来提出 issues"



@qiu_qiu.handle()
async def qiu_qiu_(bot: Bot, event: Event):
    txt = str(event.get_message()).strip().lower()
    if txt == "":
        return
    mes = qiu_qiu_word_translation(txt)
    mes += suffix
    await qiu_qiu.finish(mes,at_sender=True)



@qiu_qiu_dictionary.handle()
async def qiu_qiu_dictionary_(bot: Bot, event: Event):
    txt = str(event.get_message()).strip().lower()
    if txt == "":
        return
    mes = qiu_qiu_phrase_translation(txt)
    mes += suffix
    await qiu_qiu_dictionary.finish(mes,at_sender=True)







