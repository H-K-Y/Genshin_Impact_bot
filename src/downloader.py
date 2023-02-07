import asyncio
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from logging import Logger
from pathlib import Path
from sys import stdout
from typing import List, Union

import aiofiles
import httpx
from httpx import URL

from .utils import logger


class DownloadItem:
    def __init__(self, url: Union[str, URL], dest: Union[str, Path, None] = None, **kwargs):
        if isinstance(url, str):
            url = URL(url=url)
        if isinstance(dest, str):
            dest = Path(dest)
        self.url: URL = url
        self.trace_id = uuid.uuid4()
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
            if len(url) >= 2:
                return DownloadItem(*url[:2])
        return DownloadItem(url=url)

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

    def _download(self, dl_item: DownloadItem):
        with httpx.Client(follow_redirects=True) as client_:
            _filename = self._get_filename(dl_item)
            _resp = client_.get(dl_item.url)
            with self.lock:
                self._progress_upd()
                self._update_term_progress(_filename)
            if _resp.status_code != 200:
                return False
            dest = self._get_dest_folder(dl_item.dest) if dl_item is not None else self.dest_path
            with open(dest / _filename, 'rb') as file_:
                file_.write(_resp.read())
            return True

    async def _async_download(self, dl_item: DownloadItem):
        async with httpx.AsyncClient(follow_redirects=True) as client_:
            _filename = self._get_filename(dl_item)
            resp_ = await client_.get(dl_item.url)
            with self.lock:
                self._progress_upd()
                self._update_term_progress(_filename)
            if resp_.status_code != 200:
                return False
            dest = self._get_dest_folder(dl_item.dest) if dl_item is not None else self.dest_path
            with aiofiles.open(dest / _filename, 'rb') as file_:
                await file_.write(resp_.read())
            return True

    @property
    def len(self):
        return len(self.task_list)

    @property
    def progress(self):
        return self.finish_count / self.len

    def multi_download(self, max_connections: int = 5):  # 多线程下载  max_connections impl: _tasks[::max_connections]
        with ThreadPoolExecutor(max_workers=max_connections) as executor:
            _result = [executor.submit(self._download, dl_item=item_) for item_ in self.task_list]
        result_state = [r.done() for r in _result]
        success_count = result_state.count(True)
        if not all(result_state):
            self.logger.warning(f'下载完毕。| 成功: {success_count} 失败: {len(result_state) - success_count}')
            return False
        self.logger.info(f'下载完毕。已完成 {success_count} 个下载任务。')
        return True

    def async_multi_download(self, max_connections: int = 5):  # 异步下载
        _tasks = []
        for item_ in self.task_list:
            _tasks.append(asyncio.create_task(self._async_download(item_)))
        chunks = self._get_connection_slice(_tasks, max_connections)
        for chunk in chunks:
            _ = asyncio.gather(*chunk)

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

    def __iadd__(self, other):
        if not isinstance(other, (str, URL, httpx.URL)):
            return
        _item = DownloadItem(url=other)
        self.task_list.append(_item)
