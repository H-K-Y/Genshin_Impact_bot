from collections import UserList
from enum import Enum
from typing import Sequence, Union

import httpx
from httpx import URL

from .utils import AssetIndex, OnlineAssetIndex, logger
from .asset_manager import DownloadItem

__all__ = ['BuiltinAssets']


class CharacterAndWeaponsIndex(OnlineAssetIndex):
    def _convert_index(self) -> list:
        _data = self.raw_index[0]
        return [
            DownloadItem(url=res["icon"], dest=res_type, name=res["item_id"])
            for res_type in _data.keys() for res in _data[res_type]
        ]

    def __init__(self):
        super().__init__(
            name='Character&Weapon', description='AssetIndex of characters and weapons',
            index_url='https://waf-api-takumi.mihoyo.com/common/map_user/ys_obc/v1/map/'
                      'game_item?map_id=2&app_sn=ys_obc&lang=zh-cn'
        )


class GameMaps(OnlineAssetIndex):  # use https://api-static.mihoyo.com/common/map_user/ys_obc/v1/map/info?map_id=2&app_sn=ys_obc&lang=zh-cn
    def __init__(self):
        super().__init__(
            name='Resource_Maps', description='background of map',
            index_url=[]
        )


class BuiltinAssets(Enum):
    game_item_all = CharacterAndWeaponsIndex()
    map = GameMaps()
