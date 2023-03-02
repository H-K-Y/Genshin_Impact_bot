import json
from abc import ABC, abstractmethod
from pathlib import Path
from collections import UserDict
from typing import Callable, Optional, Union, Type, TypeVar, Dict, Literal

import tomlkit
from pydantic import BaseModel, create_model
from tomlkit import TOMLDocument
from tomlkit.items import Table, Trivia
from .utils import logger


class SimpleLoaderBase(ABC):
    def __init__(self, path: Union[str, Path], encoding: str = 'utf-8'):
        if not isinstance(path, Path):
            path = Path(Path)
        self.__path = path
        self.encoding = encoding

    @abstractmethod
    def load(self):
        ...

    @abstractmethod
    def save(self, __obj):
        ...

    @abstractmethod
    async def async_load(self):
        ...

    @abstractmethod
    async def async_save(self, __obj):
        ...


class JSONLoader(SimpleLoaderBase):
    def __dumps_data(self, __data: dict, __schema: dict):
        _result = {}
        _properties = __schema['properties']
        for k, v in _properties:
            ...


    def load(self):
        with open(self.__path, 'r', encoding=self.encoding) as _config_file:
            return json.load(_config_file)

    def save(self, __obj: 'ConfigBase'):
        _properties = __obj.schema().get('properties')
        _data = __obj.dict()
        with open(self.__path, 'w+', encoding=self.encoding) as _config_file:
            json.dump(obj=__obj, fp=_config_file, ensure_ascii=False)

    async def async_load(self):
        return self.load()

    async def async_save(self, __obj):
        return self.save(__obj)


class TomlLoader(SimpleLoaderBase):
    def load(self):
        with open(self.__path, 'r', encoding=self.encoding) as _config_file:
            return tomlkit.load(_config_file)

    def save(self, __obj):
        with open(self.__path, 'w+', encoding=self.encoding) as _config_file:
            tomlkit.dump(__obj, _config_file)

    async def async_load(self):
        return self.load()

    async def async_save(self, __obj):
        return self.save(__obj)


def get_loader(file_ext: str):
    file_ext = file_ext.lower()
    if file_ext == 'json':
        return JSONLoader
    if file_ext == 'toml':
        return TomlLoader
    return None


class ConfigBase(BaseModel):
    """
    ConfigBase.

    Example:
        class MyConfig(ConfigBase):
            foo = ConfigField(str, description="foo", default="bar")

        config = MyConfig('./config.toml')
        assert config.foo == "bar"
    """

    @staticmethod
    def __check_config_ext(path: Union[str, Path]):
        if not isinstance(path, Path):
            path = Path(path)
        _name_split = path.name.lower().split()
        if len(_name_split) <= 2:
            return None
        if _name_split[-1] in ['json', 'toml', 'conf', 'ini']:
            return _name_split[-1]
        return None

    def reload(self):
        self.__data = self.__loader.load()
        self.model = self.parse_obj(self.__data)

    def save(self):
        ...

    def __init__(self, path: Union[str, Path]):
        _loader = get_loader(self.__check_config_ext(path))
        self.__config_path = path
        self.__loader: SimpleLoaderBase = _loader(path)
        self.__data = self.__loader.load()
        self.model = super().__init__(**self.__data)
