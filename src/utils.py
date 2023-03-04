import logging
import sys

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


__all__ = [
    'logger',
    'DictSpace'
]
