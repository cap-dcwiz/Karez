from pkgutil import iter_modules

import nats


class KarezRoleBase:
    def __init__(self, config, nats_addr="nats://localhost:4222"):
        self.config = config
        self.name = config.get("name", config.type)
        self.nc_addr = nats_addr
        self.nc = None

    async def async_init(self):
        if not self.nc:
            self.nc = await nats.connect(self.nc_addr, name=self.name)


def search_plugins(file_path, name):
    library = {}
    file_path = [str(x) for x in file_path]

    for loader, module_name, is_pkg in iter_modules(file_path):
        _sub_module = loader.find_module(module_name).load_module(module_name)
        item = getattr(_sub_module, name, [])
        if item:
            library[module_name] = item

    return library


def sub_dict(dic, *keys, **renames):
    d1 = {k: v for k, v in dic.items() if k in keys}
    d2 = {renames[k]: v for k, v in dic.items() if k in renames.keys()}
    return d1 | d2
