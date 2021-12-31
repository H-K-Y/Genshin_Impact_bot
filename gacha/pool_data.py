import time

from PIL import Image, ImageFont, ImageDraw, ImageMath
from bs4 import BeautifulSoup as bs
from loguru import logger
import httpx

import os
import json
import time



FILE_PATH = os.path.dirname(__file__)
ICON_PATH = os.path.join(FILE_PATH,'icon')


POOL_API =   "https://webstatic.mihoyo.com/hk4e/gacha_info/cn_gf01/gacha/list.json"
ROLES_API = ['https://genshin.honeyhunterworld.com/db/char/characters/?lang=CHS',
             'https://genshin.honeyhunterworld.com/db/char/unreleased-and-upcoming-characters/?lang=CHS']
ARMS_API =  ['https://genshin.honeyhunterworld.com/db/weapon/sword/?lang=CHS',
             'https://genshin.honeyhunterworld.com/db/weapon/claymore/?lang=CHS',
             'https://genshin.honeyhunterworld.com/db/weapon/polearm/?lang=CHS',
             'https://genshin.honeyhunterworld.com/db/weapon/bow/?lang=CHS',
             'https://genshin.honeyhunterworld.com/db/weapon/catalyst/?lang=CHS']
ROLES_HTML_LIST = None
ARMS_HTML_LIST = None

FONT_PATH = os.path.join(os.path.dirname(FILE_PATH),'artifact_collect',"zh-cn.ttf")
FONT=ImageFont.truetype(FONT_PATH, size=20)


# 这个字典记录的是3个不同的卡池，每个卡池的抽取列表
pool = collections.defaultdict(
    lambda: {
        '5_star_UP': [],
        '5_star_not_UP': [],
        '4_star_UP': [],
        '4_star_not_UP': [],
        '3_star_not_UP': []
    })


async def fetch_data(url: str, method='text'):
    # 获取url的数据
    async with httpx.AsyncClient() as client:
        resp = await client.get(url=url, timeout=10)
        if resp.status_code != 200:
            raise ValueError(f"从 {url} 获取数据失败，错误代码 {resp.status_code}")
        return resp.text if method == 'text' else resp.content


async def get_character_icons(url):
    divs = bs(await fetch_data(url), 'html.parser').find_all('div', {"class": "char_sea_cont"})
    character_ = {}
    for div in divs:
        span_tag = div.find('span', {"class": "sea_charname"})
        element_img = div.find('img', {"class": "char_portrait_card_sea_element lazy"}).get('data-src')
        character_.update({
            span_tag.text: {
                "url": "https://genshin.honeyhunterworld.com/img/char/"
                       f"{span_tag.parent.get('href').strip('/').split('/')[2]}_face.png",
                "rarity": len(div.find_all('div', {"class": "sea_char_stars_wrap"})),
                "element": element_img[element_img.rfind('/') + 1:].split('_')[0]
            }
        })
    return character_


async def get_weapon_icons(url):
    trs = bs(await fetch_data(url), 'html.parser').find('table', {"class": "art_stat_table"}).find_all('tr')[1:]
    weapon_ = {}
    for tr in trs:
        tds = tr.find_all('td')
        a_tag = tds[2].next
        weapon_.update({
            a_tag.text: {
                "url": f"https://genshin.honeyhunterworld.com/img/weapon{a_tag.get('href')}_a.png",
                "rarity": len(tds[3].find_all('div', {"class": "stars_wrap"}))
            }
        })
    return weapon_


async def get_icon(url: str, width: int = None) -> Image.Image:
    # 获取角色或武器的图标，直接返回 Image
    icon = Image.open(BytesIO(await fetch_data(url, 'content')))
    if width:
        height = icon.size[1] / icon.size[0] * width
        icon = icon.resize((width, int(height)))
    return icon


async def paste_character_icon(chinese_name: str):
    # 拼接角色图鉴图
    character_dict = character_icons.get(chinese_name)
    t1 = time.time()
    avatar_icon = await get_icon(character_dict.get('url'), 220)
    t2 = time.time()
    element_icon = element_icons.get(character_dict['element'])
    canvas = card_bg.copy()
    bg = rarity_bg[character_dict.get('rarity') - 1].copy()
    bg.paste(avatar_icon, (10, 14), mask=avatar_icon.getchannel('A'))
    bg.paste(rarity_bar_bg, (0, 216), mask=rarity_bar_bg.getchannel('A'))
    bg.paste(element_icon, (20, 20), mask=element_icon.getchannel('A'))
    d = ImageDraw.Draw(bg)
    d.text((120, 282), chinese_name, font=FONT, fill='black', anchor='mm')
    canvas.paste(bg, mask=card_bg)
    print('Download avatar icon:', t2 - t1)
    print('Generating:', time.time() - t2)
    return canvas.crop((10, 10, 230, 310))


async def paste_weapon_icon(chinese_name: str):
    # 拼接武器图鉴图
    weapon_dict = weapon_icons.get(chinese_name)
    t1 = time.time()
    avatar_icon = await get_icon(weapon_dict.get('url'), 220)
    t2 = time.time()
    canvas = card_bg.copy()
    bg = rarity_bg[weapon_dict.get('rarity') - 1].copy()
    bg.paste(avatar_icon, (10, 14), mask=avatar_icon.getchannel('A'))
    bg.paste(rarity_bar_bg, (0, 216), mask=rarity_bar_bg.getchannel('A'))
    rarity_star = rarity_icons[weapon_dict.get('rarity') - 1]
    bg.paste(rarity_star, (45, 232), mask=rarity_star.getchannel('A'))
    d = ImageDraw.Draw(bg)
    d.text((120, 282), chinese_name, font=FONT, fill='black', anchor='mm')
    canvas.paste(bg, mask=card_bg)
    print('Download avatar icon:', t2 - t1)
    print('Generating:', time.time() - t2)
    return canvas.crop((10, 10, 230, 310))


async def init_pool_list():
    # 初始化卡池数据
    global ROLES_HTML_LIST
    global ARMS_HTML_LIST

    ROLES_HTML_LIST = None
    ARMS_HTML_LIST = None
    pool.clear()

    logger.info(f"正在更新卡池数据")
    data = await fetch_data(BANNER_API)
    data = json.loads(data.decode("utf-8"))
    for d in data["data"]["list"]:

        begin_time = time.mktime(time.strptime(d['begin_time'], "%Y-%m-%d %H:%M:%S"))
        end_time = time.mktime(time.strptime(d['end_time'], "%Y-%m-%d %H:%M:%S"))
        if not (begin_time < time.time() < end_time):
            continue

        pool_name = str(d['gacha_name'])
        pool_url = f"https://webstatic.mihoyo.com/hk4e/gacha_info/cn_gf01/{d['gacha_id']}/zh-cn.json"
        pool_data = await fetch_data(pool_url)
        pool_data = json.loads(pool_data.decode("utf-8"))

        for prob_list in ['r3_prob_list', 'r4_prob_list', 'r5_prob_list']:
            for i in pool_data[prob_list]:
                item_name = i['item_name']
                item_type = i["item_type"]
                item_star = str(i["rank"])
                key = ''
                key += item_star
                if str(i["is_up"]) == "1":
                    key += "_star_UP"
                else:
                    key += "_star_not_UP"
                pool[pool_name][key].append(item_name)

                if item_type == '角色':
                    await up_role_icon(name=item_name, star=item_star)
                else:
                    await up_arm_icon(name=item_name, star=item_star)


# 初始化
# loop = asyncio.get_event_loop()
# loop.run_until_complete(init_pool_list())

if __name__ == '__main__':
    import asyncio

    weapon_icons = {
        '无锋剑': {
            'url': 'https://genshin.honeyhunterworld.com/img/weapon/w_1001_a.png',
            'rarity': 1
        }
    }
    t3 = time.time()
    im = asyncio.run(paste_weapon_icon('无锋剑'))
    print('Call back(total):', time.time() - t3)
    im.show()
