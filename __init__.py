from nonebot import load_plugins

from pathlib import Path

_sub_plugins = set()
_sub_plugins |= load_plugins(str(Path(__file__).parent.resolve()))
