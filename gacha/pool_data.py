from PIL import Image, ImageFont, ImageDraw
from nonebot import get_driver
from loguru import logger
import httpx

import time
import asyncio
import threading
import collections
from io import BytesIO
from pathlib import Path

try:
    from bs4 import BeautifulSoup

    use_bs = True
except ModuleNotFoundError:
    import re

    use_bs = False

BANNER_API = "https://webstatic.mihoyo.com/hk4e/gacha_info/cn_gf01/gacha/list.json"
PAGE_CHARACTER = ['https://genshin.honeyhunterworld.com/db/char/characters/?lang=CHS',
                  'https://genshin.honeyhunterworld.com/db/char/unreleased-and-upcoming-characters/?lang=CHS']
PAGE_WEAPONS = ['https://genshin.honeyhunterworld.com/db/weapon/sword/?lang=CHS',
                'https://genshin.honeyhunterworld.com/db/weapon/claymore/?lang=CHS',
                'https://genshin.honeyhunterworld.com/db/weapon/polearm/?lang=CHS',
                'https://genshin.honeyhunterworld.com/db/weapon/bow/?lang=CHS',
                'https://genshin.honeyhunterworld.com/db/weapon/catalyst/?lang=CHS']

driver = get_driver()
lock = threading.Lock()
FILE_PATH = Path(__file__).parent
ASSETS_PATH = FILE_PATH / 'assets'
card_bg = Image.open(ASSETS_PATH / 'card_bg.png')
rarity_bar_bg = Image.open(ASSETS_PATH / 'rarity_bar_bg.png')
FONT = ImageFont.truetype(str(FILE_PATH.parent / 'artifact_collect' / 'zh-cn.ttf'), size=24)
rarity_bg = [Image.open(ASSETS_PATH / f'UI_QualityBg_{i}.png').resize((240, 320)) for i in range(1, 6)]
rarity_icons = [Image.open(ASSETS_PATH / f'rarity_bar_{i}.png') for i in range(1, 6)]
element_icons = {i: Image.open(ASSETS_PATH / f'{i}.png') for i in 'cryo/dendro/electro/geo/hydro/pyro/anemo'.split('/')}

character_icons = {}
weapon_icons = {}

# 这个字典记录的是3个不同的卡池，每个卡池的抽取列表
POOL = collections.defaultdict(
    lambda: {
        '5_star_UP': [],
        '5_star_not_UP': [],
        '4_star_UP': [],
        '4_star_not_UP': [],
        '3_star_not_UP': []
    })


async def fetch_data(url: str, data='normal'):
    # 获取url的数据
    async with httpx.AsyncClient() as client:
        resp = await client.get(url=url, timeout=10)
        if resp.status_code != 200:
            raise ValueError(f"从 {url} 获取数据失败，错误代码 {resp.status_code}")
        if data == 'normal':
            return resp.text
        if data == 'json':
            return resp.json()
        if data == 'obj':
            return resp
        return resp.content


async def get_character_icons(url):
    lock.acquire()
    character_ = {}
    html = await fetch_data(url)
    if use_bs:
        divs = BeautifulSoup(html, 'html.parser').find_all('div', {"class": "char_sea_cont"})
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
    else:
        characters = re.findall(r'<div class=char_sea_cont>(.*?)</a></div></div>', html, re.M | re.I)
        for c in characters:
            rarity = len(re.findall(r'<svg.*?>', c))
            character_.update({
                re.search(r'<span.*?>(.*?)</span>', c).groups()[0]: {
                    "url": "https://genshin.honeyhunterworld.com/img/char/" +
                           re.search(r'<a.+?href="/db/char/(.*?)/.+?">', c).groups()[0] + "_face.png",
                    "rarity": rarity,
                    "element": re.search(r'<img.+?element.+/img/icons/element/(.+)_35.png></a>', c).groups()[0]
                }
            })
    character_icons.update(character_)
    lock.release()


async def get_weapon_icons(url):
    lock.acquire()
    html = await fetch_data(url)
    weapon_ = {}
    if use_bs:
        trs = BeautifulSoup(html, 'html.parser').find('table', {"class": "art_stat_table"}).find_all('tr')[1:]
        for tr in trs:
            tds = tr.find_all('td')
            a_tag = tds[2].next
            weapon_.update({
                a_tag.text: {
                    "url": "https://genshin.honeyhunterworld.com/img/weapon/"
                           f"{a_tag.get('href').strip('/').split('/')[2]}_a.png",
                    "rarity": len(tds[3].find_all('div', {"class": "stars_wrap"}))
                }
            })
    else:
        weapons = list(
            filter(lambda x: 'Icon' not in x, re.findall(r'<tr><td></td>(.*?)</tr>', html, re.M | re.I)[1:])
        )
        for w in weapons:
            icon, name = re.search(r'</td><td><a.+?/db/weapon/(.+?)/\?lang=CHS">(.*)</a></td><td>', w).groups()
            rarity = len(re.findall(r'<svg.+?item_stars.+?>', w))
            weapon_.update({
                name: {
                    "url": "https://genshin.honeyhunterworld.com/img/weapon/" + icon + "_a.png",
                    "rarity": rarity
                }
            })
    weapon_icons.update(weapon_)
    lock.release()


async def init_data():
    process_queue = []
    for url in PAGE_CHARACTER:
        process_queue.append(
            threading.Thread(target=asyncio.run, args=(get_character_icons(url),))
        )
    for url in PAGE_WEAPONS:
        process_queue.append(
            threading.Thread(target=asyncio.run, args=(get_weapon_icons(url),))
        )
    for t in process_queue:
        t.start()
    for t in process_queue:
        t.join()


async def get_icon(url: str, width: int = None) -> Image.Image:
    # 获取角色或武器的图标，直接返回 Image
    icon = Image.open(BytesIO(await fetch_data(url, data='content')))
    if width:
        height = icon.size[1] / icon.size[0] * width
        icon = icon.resize((width, int(height)))
    return icon


async def save_character_icon(chinese_name: str):
    # 拼接角色图鉴图
    character_dict = character_icons.get(chinese_name)
    avatar_icon = await get_icon(character_dict.get('url'), 220)
    element_icon = element_icons.get(character_dict['element'])
    canvas = card_bg.copy()
    bg = rarity_bg[character_dict.get('rarity') - 1].copy()
    bg.paste(avatar_icon, (10, 14), mask=avatar_icon.getchannel('A'))
    bg.paste(rarity_bar_bg, (0, 216), mask=rarity_bar_bg.getchannel('A'))
    bg.paste(element_icon, (20, 20), mask=element_icon.getchannel('A'))
    d = ImageDraw.Draw(bg)
    d.text((120, 282), chinese_name, font=FONT, fill='black', anchor='mm')
    canvas.paste(bg, mask=card_bg)
    canvas.crop((10, 10, 230, 310)).save(ASSETS_PATH / '角色图鉴' / f'{chinese_name}.png')


async def save_weapon_icon(chinese_name: str):
    # 拼接武器图鉴图
    weapon_dict = weapon_icons.get(chinese_name)
    avatar_icon = await get_icon(weapon_dict.get('url'), 220)
    canvas = card_bg.copy()
    bg = rarity_bg[weapon_dict.get('rarity') - 1].copy()
    bg.paste(avatar_icon, (10, 14), mask=avatar_icon.getchannel('A'))
    bg.paste(rarity_bar_bg, (0, 216), mask=rarity_bar_bg.getchannel('A'))
    rarity_star = rarity_icons[weapon_dict.get('rarity') - 1]
    bg.paste(rarity_star, (45, 232), mask=rarity_star.getchannel('A'))
    d = ImageDraw.Draw(bg)
    d.text((120, 282), chinese_name, font=FONT, fill='black', anchor='mm')
    canvas.paste(bg, mask=card_bg)
    canvas.crop((10, 10, 230, 310)).save(ASSETS_PATH / '武器图鉴' / f'{chinese_name}.png')


async def mk_icon(name, type_='', cover=False):
    # 更新角色图标
    type_ = '角色' if type_ == '角色' else '武器'
    file_path = ASSETS_PATH / f'{type_}图鉴' / f'{name}.png'
    if not file_path.parent.exists():
        file_path.parent.mkdir()
    if file_path.exists() and not cover:
        return
    logger.info(f"正在更新 {name} {type_}图标")

    try:
        if type_ == '角色':
            await save_character_icon(name)
        else:
            await save_weapon_icon(name)
    except Exception as e:
        logger.error(f"更新 {name} {type_}图标失败，错误为 {e},建议稍后使用 更新原神卡池 指令重新更新")


@driver.on_startup
async def init_pool_list():
    POOL.clear()

    logger.info(f"正在更新卡池数据")
    data = await fetch_data(BANNER_API, data='json')
    await init_data()

    for d in data["data"]["list"]:
        begin_time = time.mktime(time.strptime(d['begin_time'], "%Y-%m-%d %H:%M:%S"))
        end_time = time.mktime(time.strptime(d['end_time'], "%Y-%m-%d %H:%M:%S"))
        if not (begin_time < time.time() < end_time):
            continue

        pool_name = str(d['gacha_name'])
        pool_url = f"https://webstatic.mihoyo.com/hk4e/gacha_info/cn_gf01/{d['gacha_id']}/zh-cn.json"
        pool_data = await fetch_data(pool_url, data='json')

        for prob_list in ['r3_prob_list', 'r4_prob_list', 'r5_prob_list']:
            process_queue = []
            for i in pool_data[prob_list]:
                item_name = i['item_name']
                item_type = i["item_type"]
                item_rarity = str(i["rank"])
                key = ''
                key += item_rarity
                key += "_star_UP" if str(i["is_up"]) == "1" else "_star_not_UP"
                POOL[pool_name][key].append(item_name)
                process_queue.append(
                    threading.Thread(target=asyncio.run, args=(mk_icon(item_name, item_type),))
                )
            for p in process_queue:
                p.start()
            for p in process_queue:
                p.join()
