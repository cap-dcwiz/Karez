from karez.config import ConfigEntity, OptionalConfigEntity
from karez.converter import ConverterBase


class Converter(ConverterBase):
    @classmethod
    def role_description(cls):
        return "Converter to format time-series points."

    @classmethod
    def config_entities(cls):
        yield from super(Converter, cls).config_entities()
        yield ConfigEntity("measurement", "Key name to be used as measurement name in TSDB.")
        yield OptionalConfigEntity("field_name", None, "Key name to be used as field name in TSDB.")
        yield OptionalConfigEntity("field_value", "value", "Key name to be used as value in TSDB.")

    def convert(self, payload):
        payload["_measurement"] = self.config.measurement
        field_name = self.config.field_name
        field_value = self.config.field_value
        if field_name:
            payload[payload[field_name]] = payload[field_value]
            del payload[field_name]
            del payload[field_value]
        yield payload
