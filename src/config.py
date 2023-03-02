from pathlib import Path
from collections import UserDict
from typing import Callable, Optional, Union, Type, TypeVar, Dict

from tomlkit import TOMLDocument
from tomlkit.items import Table, Trivia
from .utils import logger


TomlAvailType = Union[str, bool, int, float, list, tuple, dict]
TomlAvailTypes = (str, bool, int, float, list, tuple, dict)
TomlAvailClasses = TypeVar('TomlAvailClasses', bound=TomlAvailType)


class ConfigField:
    description: str
    """
    Fields of config, note that `tuple` will be automatically converted to list(array)
    """
    def __init__(self, __type: Type[TomlAvailClasses],
                 description: Optional[Union[str, None]] = None,
                 default: Optional[Union[TomlAvailType, None]] = None):
        if __type not in {str, bool, int, float, list, tuple, dict}:
            self._type = str
        else:
            self._type = __type
        self.description = description
        if isinstance(default, self._type):
            self._value = default
        else:
            self._value = self._type()

    def update(self, value: TomlAvailType):
        if isinstance(value, self._type):
            self._value = value
        else:
            self._value = self._type(value)

    def clear(self):
        self._value = self._type()

    @property
    def value(self):
        return self._value

    @property
    def type(self):
        return self._type


class BaseContainer(UserDict):
    def __init__(self, on_error: Optional[Callable] = logger.error):
        self.__on_error = on_error
        self._update_fields()
        super().__init__()

    def _update_fields(self):
        _fields = filter(lambda x: not x[0].startswith('_'), self.__class__.__dict__.items())
        for _field_name, _field_definition in _fields:
            if _field_definition in {str, bool, int, float, list, tuple}:
                self[_field_name] = ConfigField(_field_definition)
            if isinstance(_field_definition, ConfigField):
                self[_field_name] = _field_definition


class ConfigTable(BaseContainer):
    def __init__(self, **fields: Union[Type[ConfigField], Type[TomlAvailType]]):
        super().__init__()
        self._update_fields()

        for _field_name, _field_definition in fields.items():
            if _field_definition in {str, bool, int, float, list, tuple}:
                self[_field_name] = ConfigField(_field_definition)
            if isinstance(_field_definition, ConfigField):
                self[_field_name] = _field_definition


class ConfigBase(BaseContainer):
    """
    ConfigBase.

    Example:
        class MyConfig(ConfigBase):
            foo = ConfigField(str, description="foo", default="bar")

        config = MyConfig('./config.toml')
        assert config.foo == "bar"
    """
    ...
