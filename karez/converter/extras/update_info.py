import json

from ...config import ConfigEntity, OptionalConfigEntity
from ..base import ConverterBase


class Converter(ConverterBase):
    @classmethod
    def role_description(cls):
        return "Converter to add additional meta data."

    @classmethod
    def config_entities(cls):
        yield from super(Converter, cls).config_entities()
        yield ConfigEntity("info_file", "Json file contains data point meta data.")
        yield ConfigEntity("key", "Key name.")
        yield OptionalConfigEntity("remove", None, "remove fields after updating.")

    def convert(self, payload):
        with open(self.config.info_file, "r") as f:
            info = json.load(f)
        key = self.config.key
        payload.update(info[payload[key]])
        if self.config.remove:
            for key in self.config.remove.split(","):
                del payload[key.strip()]
        yield payload
