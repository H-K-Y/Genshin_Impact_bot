
from PIL import Image,ImageMath
from io import BytesIO
from loguru import logger
import json
import os
import time
import base64
import httpx
import asyncio



LABEL_URL      = 'https://api-static.mihoyo.com/common/blackboard/ys_obc/v1/map/label/tree?app_sn=ys_obc'
POINT_LIST_URL = 'https://api-static.mihoyo.com/common/blackboard/ys_obc/v1/map/point/list?map_id=2&app_sn=ys_obc'
MAP_URL        = "https://api-static.mihoyo.com/common/map_user/ys_obc/v1/map/info?map_id=2&app_sn=ys_obc&lang=zh-cn"

header = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'

FILE_PATH = os.path.dirname(__file__)

MAP_PATH = os.path.join(FILE_PATH,"icon","map_icon.jpg")
Image.MAX_IMAGE_PIXELS = None


CENTER = None
MAP_ICON = None


zoom = 0.5
resource_icon_offset = (-int(150*0.5*zoom),-int(150*zoom))


data = {
    "all_resource_type":{
        # 这个字典保存所有资源类型，
        # "1": {
        #         "id": 1,
        #         "name": "传送点",
        #         "icon": "",
        #         "parent_id": 0,
        #         "depth": 1,
        #         "node_type": 1,
        #         "jump_type": 0,
        #         "jump_target_id": 0,
        #         "display_priority": 0,
        #         "children": []
        #     },
    },
    "can_query_type_list":{
        # 这个字典保存所有可以查询的资源类型名称和ID，这个字典只有名称和ID
        # 上边字典里"depth": 2的类型才可以查询，"depth": 1的是1级目录，不能查询
        # "七天神像":"2"
        # "风神瞳":"5"

    },
    "all_resource_point_list" :[
            # 这个列表保存所有资源点的数据
            # {
            #     "id": 2740,
            #     "label_id": 68,
            #     "x_pos": -1789,
            #     "y_pos": 2628,
            #     "author_name": "✟紫灵心✟",
            #     "ctime": "2020-10-29 10:41:21",
            #     "display_state": 1
            # },
    ],
    "date":"" #记录上次更新"all_resource_point_list"的日期
}


async def download_icon(url):
    # 下载图片，返回Image对象
    async with httpx.AsyncClient() as client:
        resp = await client.get(url=url)
        if resp.status_code != 200:
            raise ValueError(f"获取图片数据失败，错误代码 {resp.status_code}")
        icon = resp.content
        return Image.open(BytesIO(icon))

async def download_json(url):
    # 获取资源数据，返回 JSON
    async with httpx.AsyncClient() as client:
        resp = await client.get(url=url)
        if resp.status_code != 200:
            raise ValueError(f"获取资源点数据失败，错误代码 {resp.status_code}")
        return resp.json()


async def up_icon_image(sublist):
    # 检查是否有图标，没有图标下载保存到本地
    id = sublist["id"]
    icon_path = os.path.join(FILE_PATH,"icon",f"{id}.png")

    if not os.path.exists(icon_path):
        logger.info(f"正在更新资源图标 {id}")
        icon_url = sublist["icon"]
        icon = await download_icon(icon_url)
        icon = icon.resize((150, 150))

        box_alpha = Image.open(os.path.join(FILE_PATH,"icon","box_alpha.png")).getchannel("A")
        box = Image.open(os.path.join(FILE_PATH,"icon","box.png"))

        try:
            icon_alpha = icon.getchannel("A")
            icon_alpha = ImageMath.eval("convert(a*b/256, 'L')", a=icon_alpha, b=box_alpha)
        except ValueError:
            # 米游社的图有时候会没有alpha导致报错，这时候直接使用box_alpha当做alpha就行
            icon_alpha = box_alpha

        icon2 = Image.new("RGBA", (150, 150), "#00000000")
        icon2.paste(icon, (0, -10))

        bg = Image.new("RGBA", (150, 150), "#00000000")
        bg.paste(icon2, mask=icon_alpha)
        bg.paste(box, mask=box)

        with open(icon_path, "wb") as icon_file:
            bg.save(icon_file)

async def up_label_and_point_list():
    # 更新label列表和资源点列表
    logger.info(f"正在更新资源点数据")
    label_data = await download_json(LABEL_URL)
    for label in label_data["data"]["tree"]:
        data["all_resource_type"][str(label["id"])] = label
        for sublist in label["children"]:
            data["all_resource_type"][str(sublist["id"])] = sublist
            data["can_query_type_list"][sublist["name"]] = str(sublist["id"])
            await up_icon_image(sublist)
        label["children"] = []

    test = await download_json(POINT_LIST_URL)
    data["all_resource_point_list"] = test["data"]["point_list"]
    data["date"] = time.strftime("%d")
    logger.info(f"资源点数据更新完成")


async def up_map():
    # 更新地图文件 并按照资源点的范围自动裁切掉不需要的地方
    # 裁切地图需要最新的资源点位置，所以要先调用 up_label_and_point_list 再更新地图
    global CENTER
    global MAP_ICON
    logger.info(f"正在更新地图数据")
    map_info = await download_json(MAP_URL)
    map_info = map_info["data"]["info"]["detail"]
    map_info = json.loads(map_info)

    map_url_list = map_info['slices'][0]
    origin = map_info["origin"]

    x_start = map_info['total_size'][1]
    y_start = map_info['total_size'][1]
    x_end = 0
    y_end = 0
    for resource_point in data["all_resource_point_list"]:
        x_pos = resource_point["x_pos"] + origin[0]
        y_pos = resource_point["y_pos"] + origin[1]
        x_start = min(x_start,x_pos)
        y_start = min(y_start,y_pos)
        x_end = max(x_end,x_pos)
        y_end = max(y_end,y_pos)

    x_start -= 200
    y_start -= 200
    x_end += 200
    y_end += 200

    CENTER = [origin[0] - x_start, origin[1] - y_start]
    x = int(x_end - x_start)
    y = int(y_end - y_start)
    MAP_ICON = Image.new("RGB",(x,y))
    x_offset = 0
    for i in map_url_list:
        map_url = i["url"]
        map_icon = await download_icon(map_url)
        MAP_ICON.paste(map_icon,
                       (int(-x_start) + x_offset, int(-y_start)))
        x_offset += map_icon.size[0]

    logger.info(f"地图数据更新完成")


async def init_point_list_and_map():
    await up_label_and_point_list()
    await up_map()



# 初始化
loop = asyncio.get_event_loop()
loop.run_until_complete(init_point_list_and_map())




class Resource_map(object):

    def __init__(self,resource_name):
        self.resource_id = str(data["can_query_type_list"][resource_name])

        # self.map_image = Image.open(MAP_PATH)
        self.map_image = MAP_ICON.copy()
        self.map_size = self.map_image.size

        # 地图要要裁切的左上角和右下角坐标
        # 这里初始化为地图的大小
        self.x_start = self.map_size[0]
        self.y_start = self.map_size[1]
        self.x_end = 0
        self.y_end = 0

        self.resource_icon = Image.open(self.get_icon_path())
        self.resource_icon = self.resource_icon.resize((int(150*zoom),int(150*zoom)))

        self.resource_xy_list = self.get_resource_point_list()

    def get_icon_path(self):
        # 检查有没有图标，有返回正确图标，没有返回默认图标
        icon_path = os.path.join(FILE_PATH,"icon",f"{self.resource_id}.png")

        if os.path.exists(icon_path):
            return icon_path
        else:
            return os.path.join(FILE_PATH,"icon","0.png")

    def get_resource_point_list(self):
        temp_list = []
        for resource_point in data["all_resource_point_list"]:
            if str(resource_point["label_id"]) == self.resource_id :
                # 获取xy坐标，然后加上中心点的坐标完成坐标转换
                x = resource_point["x_pos"] + CENTER[0]
                y = resource_point["y_pos"] + CENTER[1]
                temp_list.append((int(x),int(y)))
        return temp_list


    def paste(self):
        for x,y in self.resource_xy_list:
            # 把资源图片贴到地图上
            # 这时地图已经裁切过了，要以裁切后的地图左上角为中心再转换一次坐标
            x -= self.x_start
            y -= self.y_start
            self.map_image.paste(self.resource_icon,(x + resource_icon_offset[0] , y + resource_icon_offset[1]),self.resource_icon)


    def crop(self):
        # 把大地图裁切到只保留资源图标位置
        for x,y in self.resource_xy_list:
            # 找出4个方向最远的坐标，用于后边裁切
            self.x_start = min(x, self.x_start)
            self.y_start = min(y, self.y_start)
            self.x_end = max(x, self.x_end)
            self.y_end = max(y, self.y_end)

        # 先把4个方向扩展150像素防止把资源图标裁掉
        self.x_start -= 150
        self.y_start -= 150
        self.x_end += 150
        self.y_end += 150

        # 如果图片裁切的太小会看不出资源的位置在哪，检查图片裁切的长和宽看够不够1000，不到1000的按1000裁切
        if (self.x_end - self.x_start)<1000:
            center = int((self.x_end + self.x_start) / 2)
            self.x_start = center - 500
            self.x_end  = center +500
        if (self.y_end - self.y_start)<1000:
            center = int((self.y_end + self.y_start) / 2)
            self.y_start = center - 500
            self.y_end  = center +500

        self.map_image = self.map_image.crop((self.x_start,self.y_start,self.x_end,self.y_end))

    def get_cq_cod(self):

        if not self.resource_xy_list:
            return "没有这个资源的信息"

        self.crop()

        self.paste()

        bio = BytesIO()
        self.map_image.save(bio, format='JPEG')
        base64_str = 'base64://' + base64.b64encode(bio.getvalue()).decode()

        return f"[CQ:image,file={base64_str}]"

    def get_resource_count(self):
        return len(self.resource_xy_list)



async def get_resource_map_mes(name):

    if data["date"] !=  time.strftime("%d"):
        await init_point_list_and_map()

    if not (name in data["can_query_type_list"]):
        return f"没有 {name} 这种资源。\n发送 原神资源列表 查看所有资源名称"

    map = Resource_map(name)
    count = map.get_resource_count()

    if not count:
        return f"没有找到 {name} 资源的位置，可能米游社wiki还没更新。"

    mes = f"资源 {name} 的位置如下\n"
    mes += map.get_cq_cod()

    mes += f"\n\n※ {name} 一共找到 {count} 个位置点\n※ 数据来源于米游社wiki"

    return mes



def get_resource_list_mes():

    temp = {}

    for id in data["all_resource_type"].keys():
        # 先找1级目录
        if data["all_resource_type"][id]["depth"] == 1:
            temp[id] = []

    for id in data["all_resource_type"].keys():
        # 再找2级目录
        if data["all_resource_type"][id]["depth"] == 2:
            temp[str(data["all_resource_type"][id]["parent_id"])].append(id)

    mes = "当前资源列表如下：\n"

    for resource_type_id in temp.keys():

        if resource_type_id in ["1","12","50","51","95","131"]:
            # 在游戏里能查到的数据这里就不列举了，不然消息太长了
            continue

        mes += f"{data['all_resource_type'][resource_type_id]['name']}："
        for resource_id in temp[resource_type_id]:
            mes += f"{data['all_resource_type'][resource_id]['name']}，"
        mes += "\n"

    return mes
