import json

from karez.converter import ConverterBase


class Converter(ConverterBase):
    def convert(self, payload):
        with open(self.config.info_file, "r") as f:
            info = json.load(f)
        key = self.config.key
        payload.update(info[payload[key]])
        return payload
