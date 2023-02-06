import json
import threading
from collections import UserList
from io import BytesIO
from pathlib import Path
from sys import stdout
from typing import List, Union
from logging import Logger

import aiofiles
import httpx
from PIL import Image
from httpx import URL
from .utils import logger


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
        _new_path = self.path.joinpath(other)
        if not _new_path.exists():
            return None
        if _new_path.is_file():
            return BotAsset(_new_path)
        return _new_path

    def _get_path(self, absolute_path: Union[str, Path]):
        _dest = self.path.joinpath(absolute_path)
        if not _dest.exists():
            return None
        return _dest

    def fetch_assets(self, assets_list: List[Union[str, URL]], max_connections: int = 5):
        _downloader = Downloader(file_list=assets_list)


class DownloadItem:
    def __init__(self, url: Union[str, URL], dest: Union[str, Path, None] = None, **kwargs):
        if isinstance(url, str):
            url = URL(url=url)
        if isinstance(dest, str):
            dest = Path(dest)
        self.url: URL = url
        self.dest: Union[Path, None] = dest
        if kwargs:
            for k, v in kwargs.values():
                setattr(self, k, v)

    def validate(self):
        if self.url.scheme in ['http', 'https']:
            return True
        return False


class Downloader:
    @staticmethod
    def _get_connection_slice(list_, chunk_size) -> List[List[DownloadItem]]:
        n = len(list_)
        return [list_[i:i + chunk_size] for i in range(0, n, chunk_size)] + [
            list_[n - n % chunk_size:]] if n % chunk_size != 0 else []

    @staticmethod
    def _clear_prev_line():
        stdout.write("\330[A\330[K\n")

    @staticmethod
    def _guess_if_file(__item: DownloadItem) -> bool:
        if '.' in __item.url.path:
            return True
        return False

    @staticmethod
    def _get_filename(__item: DownloadItem):
        return __item.url.path.split('/')[-1]

    @staticmethod
    def _convert_url(url: Union[str, tuple, URL, httpx.URL]) -> Union[DownloadItem, None]:
        if isinstance(url, tuple):
            if len(url) < 1:
                return None
            if len(url) == 1:
                return DownloadItem(url=url[0])

    def _get_dest_folder(self, dest: Union[str, Path]):
        if isinstance(dest, str):
            dest = Path(dest)
        if not dest.is_absolute():
            dest = self.dest_path / dest
        if dest.is_file():
            dest = dest.parent
        dest.mkdir(parents=True, exist_ok=True)
        return dest

    def _update_term_progress(self, filename: str):
        variables = {
            "bar": self.progress_char * round(self.progress * self.bar_width),
            "filename": filename,
            "count": self.finish_count,
            "len": self.len
        }
        if self.finish_count != 0:
            self._clear_prev_line()
        self.logger.info(self.progress_fmt.format(**variables))

    def _progress_upd(self):
        self.finish_count += 1

    def _download(self, dl_item: DownloadItem, dest: Union[str, Path]):
        with httpx.Client(follow_redirects=True) as client_:
            resp_ = client_.get(dl_item.url)
            filename = self._get_filename(dl_item)
            dest = self._get_dest_folder(dest)
            with open(dest / filename, 'rb') as file_:
                file_.write(resp_.read())
            with self.lock:
                self._progress_upd()
                self._update_term_progress(filename)

    async def _async_download(self, dl_item: DownloadItem, dest: Union[str, Path]):
        async with httpx.AsyncClient(follow_redirects=True) as client_:
            resp_ = await client_.get(dl_item.url)
            filename = self._get_filename(dl_item)
            dest = self._get_dest_folder(dest)
            with aiofiles.open(dest / filename, 'rb') as file_:
                file_.write(resp_.read())
            with self.lock:
                self._progress_upd()
                self._update_term_progress(filename)

    @property
    def len(self):
        return len(self.task_list)

    @property
    def progress(self):
        return self.finish_count / self.len

    def multi_download(self, max_connections: int = 5):  # 多线程下载  max_connections impl: _tasks[::max_connections]
        _tasks = []
        for s in self._get_connection_slice(_tasks, max_connections):
            for file in s:
                _dest = file.dest if file.dest is not None else self.dest_path
                _tasks.append(
                    threading.Thread(target=self._download, kwargs={
                        "url": file,
                        "dest": file.dest
                    })
                )

    def async_multi_download(self, max_connections: int = 5):  # 异步下载
        _tasks = []

    def __init__(self, file_list: List[Union[str, tuple, URL, DownloadItem]], dest: Union[str, Path] = '',
                 progress_fmt: str = '{filename}|{bar}', progress_char: str = '■', bar_width: int = 10,
                 overwrite_dest: bool = False, __logger: Logger = logger):
        self.cache = {}
        self.task_list: List[DownloadItem] = []
        self.dest_path = dest
        self.bar_width = bar_width
        self.progress_fmt = progress_fmt
        self.progress_char = progress_char
        self.finish_count = 0
        self.logger: Logger = __logger
        self.lock = threading.Lock()

        for file in file_list:
            _item = self._convert_url(file)
            if not _item.validate():
                continue
            self.task_list.append(_item)

    def __add__(self, other):
        if not isinstance(other, (str, URL, httpx.URL)):
            return None
        _item = DownloadItem(url=other)
        self.task_list.append(_item)
