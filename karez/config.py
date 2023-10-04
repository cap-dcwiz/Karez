from loguru import logger as logging
from abc import ABC, abstractmethod
from collections.abc import Iterable
from numbers import Number
from typing import Union, TypeAlias

from dynaconf import Dynaconf


class ConfigEntityBase:
    def __init__(self, name: str):
        self.name: str = name

    @abstractmethod
    def describe(self, indent: int) -> str:
        pass


class ConfigEntity(ConfigEntityBase):
    def __init__(self, name: str, description: str = ""):
        super(ConfigEntity, self).__init__(name)
        self.description: str = description.strip(".") + "."

    def describe(self, indent):
        return f"{' ' * indent} - {self.name}: {self.description}\n"


DefaultType: TypeAlias = Union[
    Union[Number, str], ConfigEntityBase, dict, list, tuple, None
]


class OptionalConfigEntity(ConfigEntityBase):
    def __init__(self, name: str, default: DefaultType, description: str = ""):
        super(OptionalConfigEntity, self).__init__(name)
        self.default: DefaultType = default
        self.description: str = description.strip(".") + "."

    def describe(self, indent):
        if isinstance(self.default, ConfigEntityBase):
            default = f"Same as {self.default.name}"
        else:
            default = self.default
        return (
            f"{' ' * indent} - {self.name}: [Optional] {self.description}\n"
            f"{' ' * (indent * 2)}default: {default}\n"
        )


class ConfigGetter:
    def __init__(self, ins: "ConfigurableBase"):
        self.ins = ins

    def __getattr__(self, name: str):
        return self.ins.get_config(name)


class ConfigurableBase(ABC):
    def __init__(self, config: Dynaconf):
        self._config: Dynaconf = config
        self._conf_entities: dict[str, ConfigEntityBase] = {
            e.name: e for e in self.config_entities()
        }
        self._conf_getter = ConfigGetter(self)

    @classmethod
    @abstractmethod
    def config_entities(cls) -> Iterable[ConfigEntityBase]:
        return []

    def is_configured(self, item):
        return item in self._config

    def get_config(self, name: str):
        if name in self._conf_entities:
            e = self._conf_entities[name]
            if isinstance(e, ConfigEntity):
                try:
                    return self._config[name]
                except KeyError:
                    raise RuntimeError(
                        f"[{self.__class__.__name__}] Config entity {name} is required but not found."
                    )
            elif isinstance(e, OptionalConfigEntity):
                default = e.default
                if isinstance(default, ConfigEntityBase):
                    default = self.get_config(default.name)
                return self._config.get(name, default)
        else:
            logging.warning(f"Unknown config entity {name} for {self}.")

    @property
    def config(self):
        return self._conf_getter

    @classmethod
    def print_config_docs(cls, indent: int = 0):
        for e in cls.config_entities():
            if isinstance(e, ConfigEntity):
                print(e.describe(indent))
        for e in cls.config_entities():
            if isinstance(e, OptionalConfigEntity):
                print(e.describe(indent))
