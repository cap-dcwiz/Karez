import asyncio
import json

from .config import ConfigEntity, OptionalConfigEntity
from .role import KarezRoleBase


class DispatcherBase(KarezRoleBase):
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

    def divide_tasks(self, entities):
        batch_size = self.config.batch_size
        for i in range(0, len(entities), batch_size):
            yield entities[i: i + batch_size]

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
                    await self.nc.publish(f"karez.connector.{self.target}",
                                          json.dumps(_e).encode("utf-8"))
            await asyncio.sleep(self.interval)
