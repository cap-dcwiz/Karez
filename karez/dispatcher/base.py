import asyncio
from abc import abstractmethod
from collections.abc import Iterable
from typing import Generator

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

    def divide_tasks(self, entities: list) -> Generator[dict, None, None]:
        batch_size = self.config.batch_size
        for i in range(0, len(entities), batch_size):
            yield dict(tasks=entities[i: i + batch_size])

    @abstractmethod
    def load_entities(self) -> list:
        pass

    async def process(self, _) -> Iterable:
        return self.divide_tasks(self.load_entities())

    async def run(self):
        while True:
            if await self.async_ensure_init():
                for entities in await self.process(None):
                    await self.publish(self.connector_topic(self.target), entities)
            await asyncio.sleep(self.interval)
