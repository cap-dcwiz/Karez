import json

from karez.config import ConfigEntity
from karez.converter import ConverterBase


class Converter(ConverterBase):
    @classmethod
    def role_description(cls):
        return "Converter to add additional meta data."

    @classmethod
    def config_entities(cls):
        yield from super(Converter, cls).config_entities()
        yield ConfigEntity("info_file", "Json file contains data point meta data.")
        yield ConfigEntity("key", "Key name.")

    def convert(self, payload):
        with open(self.config.info_file, "r") as f:
            info = json.load(f)
        key = self.config.key
        payload.update(info[payload[key]])
        yield payload
