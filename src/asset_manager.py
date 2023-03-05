import json
from io import BytesIO
from pathlib import Path
from typing import List, Union

import aiofiles
from httpx import URL
from PIL import Image

from .asset_index import BuiltinAssets
from .downloader import Downloader, DownloadItem


class BotAsset:
    def __init__(self, path: Path):
        if not path.is_file():
            raise TypeError(f"{path} not a file")
        self.file = path

    def as_text(self, encoding='utf-8'):
        with open(self.file, 'r', encoding=encoding) as asset_:
            return asset_.read()

    def as_binary(self):
        with open(self.file, 'rb') as asset_:
            return asset_.read()

    async def async_as_binary(self):
        async with aiofiles.open(self.file, 'rb') as asset_:
            return await asset_.read()

    def as_bytestream(self):
        binary_ = self.as_binary()
        return BytesIO(binary_)

    def async_as_bytestream(self):
        binary_ = await self.async_as_binary()
        return BytesIO(binary_)

    def as_img(self):
        return Image.open(self.file)

    async def async_as_img(self):
        binary_ = await self.async_as_binary()
        return Image.open(binary_)

    def as_json(self, encoding='utf-8'):
        raw_json_ = self.as_text(encoding=encoding)
        return json.loads(raw_json_)


# 提案
# assets存储于固定目录
# 重复字体/图像单次导入

class BotAssetManager:
    def __init__(self, path: Path):
        self.path = path
        self.files = []

    def __truediv__(self, other):
        _new_path = self.path.joinpath(other)
        if not _new_path.exists():
            return None
        if _new_path.is_file():
            return BotAsset(_new_path)
        return _new_path

    def _get_path(self, relative_path: Union[str, Path]):
        _dest = self.path.joinpath(relative_path)
        if not _dest.exists():
            return None
        return _dest

    def require(self,
                asset_type: Union[BuiltinAssets, Union[str, URL, DownloadItem], List[Union[str, URL, DownloadItem]]]):
        ...

    def fetch_assets(self, assets_list: List[Union[str, URL]], max_connections: int = 5):
        _downloader = Downloader(file_list=assets_list)
        _downloader += self.files
