from datetime import datetime

from dateutil.parser import parse
from dateutil.tz import gettz

from karez.converter import ConverterBase


class Converter(ConverterBase):
    def convert(self, payload):
        tz_infos = {k: gettz(v) for k, v in self.config.tz_infos.items()}
        timestamp = payload["timestamp"]
        if timestamp:
            timestamp = parse(timestamp, tzinfos=tz_infos)
        else:
            timestamp = datetime.utcnow()
        payload["timestamp"] = datetime.timestamp(timestamp)
        return payload
