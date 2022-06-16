import json
from abc import ABC, abstractmethod

from karez.config import ConfigEntity, OptionalConfigEntity
from karez.role import RoleBase


class AggregatorBase(RoleBase, ABC):
    TYPE = "aggregrator"

    @classmethod
    def config_entities(cls):
        yield from super(AggregatorBase, cls).config_entities()
        yield ConfigEntity("category", "Category of data points to be aggregated.")
        yield OptionalConfigEntity("json", True, "Whether the received data is json serialized or not.")

    @property
    def subscribe_topic(self):
        return f"karez.{self.config.category}.>"

    @property
    def subscribe_queue(self):
        return f"{self.config.category}"

    async def _subscribe_handler(self, msg):
        payload = msg.data.decode("utf-8")
        if self.config.json:
            payload = json.loads(payload)
        self.process(payload)

    @abstractmethod
    def process(self, payload):
        pass
