from collections import UserList
from enum import Enum
from typing import Sequence, Union

from httpx import URL

from .asset_manager import DownloadItem

__all__ = ['BuiltinAssets']


class BuiltinAssetBase(UserList):
    type: str
    description: str


class BuiltinAssetGroup(BuiltinAssetBase):
    def __init__(self, asset_type: str, description: str, urls: Sequence[Union[str, URL, DownloadItem]]):
        self.type = asset_type
        self.description = description
        super().__init__(urls)


class GameItems(
    BuiltinAssetBase):  # use https://waf-api-takumi.mihoyo.com/common/map_user/ys_obc/v1/map/game_item?map_id=2&app_sn=ys_obc&lang=zh-cn
    def _fetch_index(self):
        ...


class GameMaps(
    BuiltinAssetBase):  # use https://api-static.mihoyo.com/common/map_user/ys_obc/v1/map/info?map_id=2&app_sn=ys_obc&lang=zh-cn
    def _get_map_index(self):
        ...


class BuiltinAssets(Enum):
    game_item_all = GameItems()
    map = GameMaps()
