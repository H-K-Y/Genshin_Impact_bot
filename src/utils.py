import asyncio
import logging
import sys
from abc import ABC
from pathlib import Path
from collections import UserList
from typing import List, Sequence, Tuple, Union, Optional

import httpx
from httpx import URL
from .downloader import convert_url, DownloadItem

logger: logging.Logger = logging.getLogger('GI Bot')
default_handler = logging.StreamHandler(sys.stdout)
default_handler.setFormatter(
    logging.Formatter('[%(asctime)s %(name)s] %(levelname)s: %(message)s'))
logger.addHandler(default_handler)


class DictSpace:
    def __parse_item(self, __obj, loo: bool = False):
        if isinstance(__obj, dict):
            return DictSpace(__obj, list_of_obj=loo)
        if isinstance(__obj, list) and loo:
            return self.__parse_list(__obj, loo=loo)
        return __obj

    def __parse_list(self, __list: list, loo: bool = False):
        return [self.__parse_item(item_, loo=loo) for item_ in __list]

    def __init__(self, __obj: dict, list_of_obj: bool = False):
        for k, v in __obj.items():
            setattr(self, k, self.__parse_item(v, loo=list_of_obj))

    def __repr__(self):
        _keys = list(filter(lambda x: not x.startswith('__'), self.__dir__()))
        if len(_keys) > 3:
            _formatted = ' '.join(f'{k}: {getattr(self, k)}' for k in _keys[:3]) + ' ...'
        else:
            _formatted = ' '.join(f'{k}: {getattr(self, k)}' for k in _keys)
        return f'<DictSpace {_formatted}>'


class AssetIndexBase(UserList):
    name: str
    description: str


class AssetIndex(AssetIndexBase):
    def __init__(self, name: Optional[str] = '', description: Optional[str] = '',
                 *url: Union[str, URL, DownloadItem, Tuple[Union[str, URL, DownloadItem], Union[str, Path]]]):
        self.name = name
        self.description = description
        if not all(isinstance(u_, DownloadItem) for u_ in url):
            url = [convert_url(u) for u in url if not isinstance(u, DownloadItem)]
        super().__init__(url)


class OnlineAssetIndex(AssetIndexBase):
    def __init__(self, name: Optional[str] = '', description: Optional[str] = '',
                 index_url: Union[str, URL, Sequence[Union[str, URL]], None] = None):
        self.name = name
        self.description = description
        _urls = index_url if not isinstance(index_url, (str, URL)) else [index_url]
        self.index_url = [
            url if isinstance(index_url, URL) else URL(url) for url in _urls
        ]
        if not index_url:
            super().__init__()
        else:
            super().__init__(self._convert_index())

    @property
    def raw_index(self) -> List[httpx.Response]:
        """
        fetch data from `index_url`
        :return: json of response or empty dict
        """
        if len(set(url.host for url in self.index_url)):  # the same host
            _base_url = self.index_url[0]
            async with httpx.AsyncClient(follow_redirects=True,
                                         base_url=f'{_base_url.scheme}://{_base_url.host}') as client_:
                async def fetch_index(url_path: str, __pos=0) -> httpx.Response:
                    if len(self.index_url) == 1:
                        logger.info(f"获取资源索引中: {self.name} ...")
                    else:
                        logger.info(f"获取资源索引中: {self.name}[{pos + 1}/{len(self.index_url)}] ...")
                    return await client_.get(url_path)

                tasks = [fetch_index(url, pos) for pos, url in enumerate(self.index_url)]
                return list(await asyncio.gather(*tasks, return_exceptions=True))

        _result = []
        for pos, url_ in enumerate(self.index_url):
            if len(self.index_url) == 1:
                logger.info(f"获取资源索引中: {self.name} ...")
            else:
                logger.info(f"获取资源索引中: {self.name}[{pos + 1}/{len(self.index_url)}] ...")
            _resp = httpx.get(url_)
            if _resp.status_code != 200:
                continue
            _result.append(_resp)
        return _result

    def _convert_index(self) -> list:
        return list(*r for r in self.raw_index)


__all__ = [
    'logger',
    'DictSpace',
    'AssetIndex',
    'OnlineAssetIndex'
]
