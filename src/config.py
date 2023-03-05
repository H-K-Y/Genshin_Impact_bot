from pathlib import Path
from typing import Any, Tuple, Type, Union, TypeVar, Optional

import tomlkit
from pydantic import BaseModel, PrivateAttr, ValidationError
from pydantic.error_wrappers import ErrorWrapper
from tomlkit import TOMLDocument, comment

__all__ = ['ConfigBase']
Model = TypeVar('Model', bound='BaseModel')


class ConfigBase(BaseModel):
    """
    ConfigBase. Note that due to problems with the upstream `tomlkit`,
    you may not be able to add comments to the bool type or table.

    Example:
        class MyConfig(ConfigBase):
            foo: str = Field('bar', description="foo")

        config = MyConfig('./config.toml')
        assert config.foo == "bar"

    Also support:
        class ConfTable(BaseModel):
            table_member: int = 1

        class MyConfig(ConfigBase):
            foo: str = Field('bar', description="foo")
            table1: ConfTable = ConfTable()
    """
    __config_path: Path = PrivateAttr(Path('./config.toml'))
    __toml_document: TOMLDocument = PrivateAttr(TOMLDocument())

    class Config:
        anystr_strip_whitespace = True
        use_enum_values = True
        validate_assignment = True

    def _model2conf(self, _data: BaseModel) -> TOMLDocument:
        _result = TOMLDocument()
        for k, v in _data.__fields__.items():
            _key = v.field_info.alias if v.field_info.alias else k
            if issubclass(v.type_, BaseModel):
                _result[_key] = self._model2conf(_data.__getattribute__(k))
            else:
                _result[_key] = _data.__getattribute__(k)
            if v.field_info.description:
                _result.item(_key).comment(v.field_info.description)
        return _result

    def load(self, config_path: Optional[Path] = None) -> TOMLDocument:
        """
        Load from toml file.

        :param config_path: Path object
        :return: TOMLDocument object
        """
        if not config_path:
            config_path = self.__config_path
        if not config_path.exists():
            self.save(config_path)
        with open(config_path, 'r', encoding='utf-8') as _config:
            _document = tomlkit.load(_config)
        self.__toml_document = _document
        if set(_document) ^ set(self.__toml_document):  # modify the toml file when the configuration key changed
            self.save()
        return _document

    def reload(self) -> Tuple[Path, TOMLDocument]:
        """
        Reload the configuration.
        """
        self.load()
        self.parse_obj(self.__toml_document)
        return self.__config_path, self.__toml_document

    def save(self, file_path: Optional[Path] = None):
        """
        Save the configuration file to specified file path.
        :param file_path: Path object
        """
        _conf_doc = TOMLDocument()
        _doc_desc = self.schema().get('description', None)
        if _doc_desc and _doc_desc != ConfigBase.schema().get('description', None):
            _conf_doc.add(comment(_doc_desc))
        _conf_doc.update(self._model2conf(self))
        self.__toml_document = _conf_doc
        if not file_path:
            file_path = self.__config_path
        if not file_path.parent.exists():
            file_path.mkdir(parents=True)
        with open(file_path, 'w+', encoding='utf8') as _config:
            tomlkit.dump(_conf_doc, _config)

    def parse_obj(self: Type['Model'], obj: Any) -> 'Model':
        """
        Fix the problem in the parse_obj of the parent class after modifying the __init__ method
        :param obj: Any object
        :return: Model
        """
        obj = self._enforce_dict_if_root(obj)
        if not isinstance(obj, dict):
            try:
                obj = dict(obj)
            except (TypeError, ValueError) as e:
                exc = TypeError(f'{self.__name__} expected dict not {obj.__class__.__name__}')
                raise ValidationError([ErrorWrapper(exc, loc='__root__')], self) from e
        return super().__init__(**dict(self.__toml_document))

    def __init__(self, path: Union[str, Path]):
        """
        Initialize the Config object from the given path
        :param path: string or Path object
        """
        if not isinstance(path, Path):
            path = Path(path)
        if not path.exists():
            super().__init__()
            self.save(path)
        self.__config_path = path
        _document = self.load()
        super().__init__(**dict(_document))
        self.__config_path = path
        self.__toml_document = _document
