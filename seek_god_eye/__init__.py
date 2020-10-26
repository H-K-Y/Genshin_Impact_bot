from hoshino import Service
from nonebot import on_command
from ..config import ALLOW_PRIVATE_CHAT
from .seek_god_eye import (JSON_LIST,
                           init_uid_info,
                           get_random_god_eye_id,
                           get_god_eye_message,
                           found_god_eye,
                           delete_god_eye_info,
                           reset_god_eye_info)


# sv = Service('原神神瞳信息查询')
#
# search_god_eye_command = []
# for eye_type in JSON_LIST:
#     search_god_eye_command.append(f"找{eye_type}")
#
# @sv.on_prefix(search_god_eye_command)
# async def search_god_eye(bot, ev):
#     god_eye_id = ev.message.extract_plain_text().strip()























