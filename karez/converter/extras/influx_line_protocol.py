from influxdb_client import Point, WritePrecision

from ...config import ConfigEntity, OptionalConfigEntity
from ..base import ConverterBase


class Converter(ConverterBase):
    @classmethod
    def role_description(cls):
        return "Format data to InfluxDB line protocol."

    @classmethod
    def config_entities(cls):
        yield from super(Converter, cls).config_entities()
        yield ConfigEntity("measurement", "Key name to be used as measurement name in TSDB.")
        yield OptionalConfigEntity("field_name", None, "Key name to be used as field name in TSDB.")
        yield OptionalConfigEntity("field_value", "value", "Key name to be used as value in TSDB.")

    def convert(self, payload):
        p = Point\
            .measurement(self.config.measurement)\
            .time(int(payload["timestamp"] * 1e9),
                  write_precision=WritePrecision.NS)
        payload.pop("timestamp")
        field_name = self.config.field_name
        field_value = self.config.field_value
        if field_name:
            p = p.field(payload[field_name], payload[field_value])
            payload.pop(field_name)
        else:
            p = p.field("value", payload[field_value])
        payload.pop(field_value)
        for k, v in payload.items():
            if not k.startswith("_"):
                p = p.tag(k, v)
        yield dict(_as_is=p.to_line_protocol())
