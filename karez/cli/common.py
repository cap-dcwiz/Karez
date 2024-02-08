import sys
from copy import copy
from enum import Enum
from pathlib import Path
from pkgutil import iter_modules
from typing import Optional

from loguru import logger

from karez.plugins import BUILTIN_PLUGINS


class PluginType(str, Enum):
    dispatcher = "dispatcher"
    connector = "connector"
    converter = "converter"
    aggregator = "aggregator"


def search_plugins(plugin_path, name):
    library = copy(BUILTIN_PLUGINS.get(name))
    file_path = [str(Path(plugin_path, name))]

    for loader, module_name, is_pkg in iter_modules(file_path):
        _sub_module = loader.find_module(module_name).load_module(module_name)
        item = getattr(_sub_module, name.capitalize(), [])
        if item:
            library[module_name] = item

    return library


def config_logger(
    level: str,
    folder: Optional[Path] = None,
    rotation: str = "90 day",
):
    logging_level = level.upper()
    common_opts = dict(
        level=logging_level,
        backtrace=logging_level == "DEBUG",
        diagnose=logging_level == "DEBUG",
        enqueue=True,
    )
    logger.remove()
    logger.add(sys.stderr, colorize=True, **common_opts)
    if folder:
        folder.mkdir(parents=True, exist_ok=True)
        logger.add(
            str(folder / f"{logging_level.lower()}.log"),
            rotation=rotation,
            **common_opts,
        )
    return logger
