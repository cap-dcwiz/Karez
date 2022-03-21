import asyncio
import json
from abc import abstractmethod
from collections.abc import Iterable

from karez.config import ConfigEntity, OptionalConfigEntity
from karez.role import RoleBase


class DispatcherBase(RoleBase):
    TYPE = "dispatcher"

    def __init__(self, *args, **kwargs):
        super(DispatcherBase, self).__init__(*args, **kwargs)
        self.interval = self.config.interval
        self.target = self.config.connector

    @classmethod
    def config_entities(cls):
        yield from super(DispatcherBase, cls).config_entities()
        yield ConfigEntity("interval", "Collection interval.")
        yield ConfigEntity("connector", "Connector to use.")
        yield OptionalConfigEntity("batch_size", 1, "Batch Size")
        yield OptionalConfigEntity("entities", None, "Entities")
        yield OptionalConfigEntity("entity_file", None, "Entity file")

    @abstractmethod
    def divide_tasks(self, entities: Iterable) -> Iterable[Iterable]:
        pass

    def _read_entities(self):
        if self.is_configured("entities"):
            entities = self.config.entities
        elif self.is_configured("entity_file"):
            with open(self.config.entity_file, "r") as f:
                entities = json.load(f)
        else:
            raise RuntimeError("Cannot load entities.")
        return entities

    async def run(self):
        while True:
            if await self.async_ensure_init():
                entities = self._read_entities()
                for _e in self.divide_tasks(entities):
                    await self.nc.publish(self.connector_topic(self.target),
                                          json.dumps(_e).encode("utf-8"))
            await asyncio.sleep(self.interval)


