from karez.converter import ConverterBase


class Converter(ConverterBase):
    def convert(self, payload):
        payload["_measurement"] = self.config.measurement
        return payload
