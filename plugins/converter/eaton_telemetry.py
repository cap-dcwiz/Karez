from karez.converter import ConverterBase


class Converter(ConverterBase):
    def convert(self, payload):
        value = payload["value"]
        if value is None:
            return
        try:
            if payload["value_type"] == 2:
                value = int(value)
            elif payload["value_type"] == 3:
                value = float(value)
            else:
                return
            payload[payload["ma_name"]] = value

            del payload["value_type"]
            del payload["value"]
            del payload["ma_name"]

            return payload
        except:
            pass
