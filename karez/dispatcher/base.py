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

    def divide_tasks(self, entities: list) -> Iterable[Iterable]:
        batch_size = self.config.batch_size
        for i in range(0, len(entities), batch_size):
            yield entities[i: i + batch_size]

    @abstractmethod
    def load_entities(self) -> list:
        pass

    async def process(self, _) -> Iterable:
        return self.divide_tasks(self.load_entities())

    async def run(self):
        while True:
            if await self.async_ensure_init():
                for _e in await self.process(None):
                    await self.nc.publish(self.connector_topic(self.target),
                                          json.dumps(_e).encode("utf-8"))
            await asyncio.sleep(self.interval)
