from karez.converter import ConverterBase


class Converter(ConverterBase):
    def convert(self, payload):
        payload["_measurement"] = self.config.measurement
        field_name = self.config.get("field_name", None)
        field_value = self.config.get("field_value", "value")
        if field_name:
            payload[payload[field_name]] = payload[field_value]
            del payload[field_name]
            del payload[field_value]
        return payload
