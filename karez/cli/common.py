from pathlib import Path
from pkgutil import iter_modules


def search_plugins(plugin_path, name):
    library = {}
    file_path = [str(Path(plugin_path, name))]

    for loader, module_name, is_pkg in iter_modules(file_path):
        _sub_module = loader.find_module(module_name).load_module(module_name)
        item = getattr(_sub_module, name.capitalize(), [])
        if item:
            library[module_name] = item

    return library
