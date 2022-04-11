from datetime import datetime

from dateutil.parser import parse
from dateutil.tz import gettz

from karez.config import ConfigEntity
from karez.converter import ConverterBase


class Converter(ConverterBase):
    @classmethod
    def role_description(cls):
        return "Converter to add or format timestamp."

    @classmethod
    def config_entities(cls):
        yield from super(Converter, cls).config_entities()
        yield ConfigEntity("tz_infos", "tz_infos as a dict. See dateutil.parser.parse.")

    def convert(self, payload):
        tz_infos = {k: gettz(v) for k, v in self.config.tz_infos.items()}
        timestamp = payload.get("timestamp", None)
        if timestamp:
            timestamp = parse(timestamp, tzinfos=tz_infos)
        else:
            timestamp = datetime.utcnow()
        payload["timestamp"] = datetime.timestamp(timestamp)
        yield payload
