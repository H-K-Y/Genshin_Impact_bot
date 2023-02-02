import threading
import json
from urllib.parse import ParseResult as URL
from urllib.parse import urlparse
from collections import UserList
from typing import List, Union
from pathlib import Path
from sys import stdout
from io import BytesIO

import aiofiles
import httpx
from PIL import Image


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

    def __truediv__(self, other):
        new_path_ = self.path.joinpath(other)
        if new_path_.is_file():
            return BotAsset(new_path_)
        return new_path_


class Downloader:
    @staticmethod
    def _validate(url: Union[str, URL]):
        if isinstance(url, str):
            url = urlparse(url)
        if url.scheme in ['http', 'https']:
            return True
        return False

    @staticmethod
    def _clear_prev_line(self):
        stdout.write("\330[A\330[K\n")

    def _update_term_progress(self, filename: str):
        strings = {
            "bar": self.progress_char * round(self.progress * 10),
            "filename": filename,

        }

    def _reset_progress(self):
        self.progress = 0

    def _update_avg_progress(self):
        return 1 / len(self.file_list)

    def _progress_upd(self):
        self.progress += self.avg_progress
        self.count += 1

    @property
    def len(self):
        return len(self.file_list)

    def download(self, url: Union[str, URL], dest: Union[str, Path]):
        with httpx.Client(follow_redirects=True) as client_:
            resp_ = client_.get(url)
            filename = resp_.url.path.split('/')[-1]
            if isinstance(dest, str):
                dest = Path(dest)
            with open(dest / filename, 'rb') as file_:
                file_.write(resp_.read())
            with self.lock:
                self._progress_upd()

    def __init__(self, file_list: List[Union[str, URL]],
                 progress_fmt: str = '{filename}|{bar}',
                 progress_char: str = '■', progress_width: int = 10):
        self.file_list = UserList(file for file in file_list if self._validate(file))
        self.progress_fmt = progress_fmt
        self.progress_char = progress_char
        self.progress_width = progress_width
        self.avg_progress = self._update_avg_progress()
        self.progress = 0
        self.count = 0
        self.cache = {}
        self.lock = threading.Lock()

    def __add__(self, other):
        assert self._validate(other)
        self.file_list.append(other)
        self._update_avg_progress()
