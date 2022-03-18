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
            payload["value"] = value
            del payload["value_type"]

            return payload
        except:
            pass
