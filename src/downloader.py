import asyncio
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from logging import Logger
from pathlib import Path
from sys import stdout
from typing import Iterable, List, Optional, Union, Set, Any

import aiofiles
import httpx
from httpx import URL

from .utils import logger

__all__ = ['DownloadItem', 'Downloader', 'convert_url']


def convert_url(url: Union[str, tuple, URL, httpx.URL]) -> Union['DownloadItem', None]:
    if isinstance(url, tuple):
        if len(url) < 1:
            return None
        if len(url) == 1:
            return DownloadItem(url=url[0])
        if len(url) >= 2:
            return DownloadItem(*url[:2])
    return DownloadItem(url=url)


class DownloadItem:
    def __init__(self, url: Union[str, URL], dest: Optional[Union[str, Path, None]] = None,
                 overwrite: Optional[bool] = True, name: Optional[Union[Any, None]] = None):
        if isinstance(url, str):
            url = URL(url=url)
        if isinstance(dest, str):
            dest = Path(dest)
        assert self.validate()
        self.url: URL = url
        self.name = name if isinstance(name, str) else str(name)
        self.trace_id = uuid.uuid4()
        self.dest: Union[Path, None] = dest
        self.overwrite = overwrite

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
            if len(__item.url.path.split('.')) >= 2:
                return True
        return False

    @staticmethod
    def _get_filename(__item: DownloadItem):
        if __item.name:
            if any(len(_item_name) == 0 for _item_name in __item.name.split('.')):
                _filename = '.'.join([*__item.name.split('.')[:-1], __item.url.path.split('/')[-1].split('.')[-1]])
                if __item.name.startswith('.'):
                    return f'.{_filename}'
                return _filename
            return __item.name
        return __item.url.path.split('/')[-1]

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

    def _download(self, dl_item: DownloadItem) -> Union[httpx.Response, None]:
        with httpx.Client(follow_redirects=True) as client_:
            _filename = self._get_filename(dl_item)
            _resp = client_.get(dl_item.url)
            with self.lock:
                self._progress_upd()
                self._update_term_progress(_filename)
            if _resp.status_code != 200:
                return None
            dest = self._get_dest_folder(dl_item.dest) if dl_item is not None else self.dest_path
            if dest.exists() and not self.overwrite_dest:
                return _resp
            with open(dest / _filename, 'rb') as file_:
                file_.write(_resp.read())
            return _resp

    async def _async_download(self, dl_item: DownloadItem) -> Union[httpx.Response, None]:
        async with httpx.AsyncClient(follow_redirects=True) as client_:
            _filename = self._get_filename(dl_item)
            _resp = await client_.get(dl_item.url)
            with self.lock:
                self._progress_upd()
                self._update_term_progress(_filename)
            if _resp.status_code != 200:
                return None
            dest = self._get_dest_folder(dl_item.dest) if dl_item is not None else self.dest_path
            if dest.exists() and not self.overwrite_dest:
                return _resp
            with aiofiles.open(dest / _filename, 'rb') as file_:
                await file_.write(_resp.read())
            return _resp

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
            self.logger.warning(f'[多线程]下载完毕。| 成功: {success_count} 失败: {len(result_state) - success_count}')
            return False
        self.logger.info(f'[多线程]下载完毕。已完成 {success_count} 个下载任务。')
        return True

    def async_multi_download(self, max_connections: int = 5):  # 异步下载
        _tasks = [asyncio.create_task(self._async_download(item_)) for item_ in self.task_list]
        _chunks = self._get_connection_slice(_tasks, max_connections)
        _results = []
        for chunk in _chunks:
            _results.append(await asyncio.gather(*chunk, return_exceptions=True))
        result_state = [r is not None for r in _results]
        success_count = result_state.count(True)
        if not all(result_state):
            self.logger.warning(f'[异步]下载完毕。| 成功: {success_count} 失败: {len(result_state) - success_count}')
            return False
        self.logger.info(f'[异步]下载完毕。已完成 {success_count} 个下载任务。')
        return True

    def __init__(self, name: Optional[str] = 'Downloader', dest: Union[str, Path] = '',
                 progress_fmt: str = '{filename}|{bar}', progress_char: str = '■', bar_width: int = 10,
                 overwrite_dest: bool = False, __logger: Logger = logger, *url: Union[str, tuple, URL, DownloadItem]):
        if not isinstance(dest, Path):
            dest = Path(dest)
        self.name = name
        self.cache = {}
        self.dest_path = dest
        self.overwrite_dest = overwrite_dest
        self.task_list: Set[DownloadItem] = set()

        self.bar_width = bar_width
        self.progress_fmt = progress_fmt
        self.progress_char = progress_char
        self.finish_count = 0

        self.logger: Logger = __logger
        self.lock = threading.Lock()

        self.task_list.update(convert_url(url_) for url_ in url if not isinstance(url_, DownloadItem))

    def __iadd__(self, other):
        if isinstance(other, Iterable):
            self.task_list.update(convert_url(url) for url in other)
        if isinstance(other, (str, URL, httpx.URL)):
            self.task_list.add(DownloadItem(url=other))
