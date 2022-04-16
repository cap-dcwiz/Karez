from copy import copy
from pathlib import Path
from pkgutil import iter_modules
from karez.plugins import BUILTIN_PLUGINS


def search_plugins(plugin_path, name):
    library = copy(BUILTIN_PLUGINS.get(name))
    file_path = [str(Path(plugin_path, name))]

    for loader, module_name, is_pkg in iter_modules(file_path):
        _sub_module = loader.find_module(module_name).load_module(module_name)
        item = getattr(_sub_module, name.capitalize(), [])
        if item:
            library[module_name] = item

    return library
