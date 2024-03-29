import json
from abc import abstractmethod

from karez.config import OptionalConfigEntity
from karez.role import RoleBase


class ConverterBase(RoleBase):
    TYPE = "converter"

    @classmethod
    def config_entities(cls):
        yield from super(ConverterBase, cls).config_entities()
        yield OptionalConfigEntity("next", None, "Next Converters to be used.")

    async def _subscribe_handler(self, msg):
        payload = msg.data.decode("utf-8")
        self.log("trace", f"Received message: {payload[:36]}")
        data = json.loads(payload)
        result = list(await self.process(data))
        next_converters = self.config.next
        if next_converters:
            if isinstance(next_converters, str):
                next_converters = [next_converters]
            for converter in next_converters:
                if converter:
                    topic = self.converter_topic(converter)
                    for item in result:
                        await self.publish(topic, self.copy_meta(item, data))
                else:
                    for item in result:
                        item = self.copy_meta(item, data)
                        await self.publish(self.aggregator_topic(item), item)
        else:
            for item in result:
                item = self.copy_meta(item, data)
                await self.publish(self.aggregator_topic(item), item)

    @abstractmethod
    def convert(self, payload: dict) -> None | dict[dict | str]:
        pass

    async def process(self, payload):
        try:
            return self.convert(payload)
        except Exception as e:
            self.log_exception(e)
            return []
